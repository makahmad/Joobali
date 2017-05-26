from django.http import HttpResponse
from enrollment import enrollment_util
from manageprogram import program_util
from invoice import invoice_util
from parent import parent_util
from login import provider_util
from login.models import Provider
from invoice.models import Invoice, InvoiceLineItem
from google.appengine.ext import ndb
from datetime import datetime, date
from datetime import timedelta
from common.dwolla import parse_webhook_data
from common.dwolla import get_funding_transfer, get_funded_transfer, get_funding_source
from common.dwolla import get_general
from common.email.invoice import send_invoice_email
from common.email.dwolla import send_payment_success_email, send_payment_failure_email, send_funding_source_removal_email, send_funding_source_addition_email, send_payment_created_email, send_payment_cancelled_email
from common.dwolla import start_webhook, clear_webhook
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from funding import funding_util
from dwollav2.error import ValidationError
from models import DwollaEvent
from payments.models import Payment
import logging
import json

logger = logging.getLogger(__name__)

def invoice_calculation(request):
    today = date.today()

    logger.info("LATE FEE CALCULATION")
    # loop over invoices...
    for invoice in Invoice.query().fetch():
        provider = invoice.provider_key.get()
        if invoice.late_fee_enforced and not invoice.is_paid() and invoice.due_date + timedelta(days=provider.graceDays if provider.graceDays >= 0 else 0) < today and not invoice_util.get_invoice_late_fee_added(invoice):
            program = invoice_util.get_invoice_program(invoice)
            enrollment = invoice_util.get_invoice_enrollment(invoice)
            provider = provider_util.get_provider_by_email(invoice.provider_email)
            lateFee = program.lateFee if program and program.lateFee else provider.lateFee
            if lateFee != 0:
                invoice_util.create_invoice_line_item(enrollment.key if enrollment else None, invoice, program, None, None, "Late Fee", lateFee)

            invoice.amount = invoice_util.sum_up_amount_due(invoice)
            invoice.put()

    logger.info("PAYMENT CALCULATION")
    # loop over invoices...
    for invoice in Invoice.query().fetch():
        if not invoice.is_paid():
            logger.info("Considering payment for child: %s" % invoice.child_key)
            for payment in Payment.query(Payment.child_key==invoice.child_key).fetch():
                if not payment.invoice_key or payment.invoice_key and payment.invoice_key == invoice.key:
                    if payment.balance > 0:
                        logger.info("Making payment: %s" % invoice)
                        invoice_util.pay(invoice, payment)


    logger.info("INVOICE CALCULATION")
    invoice_dict = dict() # a map from provider-child pair to invoice
    days_before = 5
    # loop over providers...
    providers = Provider.query().fetch()
    for provider in providers:
        logger.info("Calculating invoices for provider: %s" % provider)

        enrollments = enrollment_util.list_enrollment_object_by_provider(provider.key.id())
        for enrollment in enrollments:
            if enrollment.status != 'active':
                logger.info("Enrollment not active. Skipping invoice calc: %s" % enrollment)
                continue
            logger.info("Calculating invoice for enrollment: %s" % enrollment)

            child_key = enrollment.child_key
            program_key = enrollment.program_key
            child = child_key.get()
            program = program_key.get()

            due_date = enrollment.start_date

            should_proceed = False # whether we should generate a invoice for this enrollment now
            program_cycle_time = None # either a weekly cycle or a monthly cycle
            if program.billingFrequency != 'Weekly' and  program.billingFrequency != 'Monthly':
                logger.info("Skipping invoice calculation. Unexpected program cycle: %s" % program)
                should_proceed = False

            # Enrollment first billing date must be after program start date. This should be enforced by UI.
            while due_date < program.startDate:
                due_date = invoice_util.get_next_due_date(due_date, program.billingFrequency)
            # find the upcomming due date in adding bill cycles to the enrollment start date until it passes today
            while due_date < today:
                due_date = invoice_util.get_next_due_date(due_date, program.billingFrequency)

            if enrollment.end_date:
                if due_date > enrollment.end_date:
                    logger.info("Enrollment already ended (current due date: %s, enrollment end date: %s). Skipping invoice calc for enrollment: %s" % (due_date, enrollment.end_date, enrollment))
                    continue
            elif program.endDate:
                logger.info(
                    "Error: enrollment doesn't have end date while program has end date of (%s): enrollment is %s" % (
                        program.endDate, enrollment))
                continue
            # should_add_registration_fee = False # if it's first invoice, we should add registration fee
            # if due_date == program_util.get_first_bill_due_date(program):
            #     should_add_registration_fee = True

            enrollment_key = ndb.Key("Provider", provider.key.id(), "Enrollment", enrollment.key.id())
            if due_date - timedelta(days=5) <= today: # 5 days ahead billing before due date
                should_proceed = True
                for invoice_line_item in InvoiceLineItem.query(InvoiceLineItem.enrollment_key == enrollment_key, InvoiceLineItem.start_date != None).fetch(): # line item without start date are adjustments
                    invoice = invoice_line_item.key.parent().get()
                    if invoice.due_date == due_date:
                        # if there is a existing invoice for this enrollment that have the same due date
                        # only proceed if current enrollment haven't yield a invoice for current billing cycle
                        logger.info("Skipping...Invoice has already been calculated for this cycle for enrollment: %s" % enrollment)
                        should_proceed = False
            else:
                logger.info("Skipping, due date too far away: today - %s, due date - %s" % (today, due_date))

            # figure out the current cycle period, which is the program cycle period overlapping with current due date
            #while cycle_start_date + program_cycle_time <= due_date:
            #    cycle_start_date += program_cycle_time

            cycle_end_date = invoice_util.get_next_due_date(due_date, program.billingFrequency) - timedelta(days=1)
            if should_proceed:
                logger.info("Calculating Invoice: program: %s, child: %s" % (program, child))

                provider_child_pair_key = str(provider.key.id()) + str(child.key.id()) + str(due_date)
                invoice = None
                # for a single day, only generate one invoice per provider-child-duedate pair.
                # the single invoices can have multiple line items if the child enrolled in multiple programs.
                if provider_child_pair_key in invoice_dict:
                    invoice = invoice_dict[provider_child_pair_key]
                else:
                    invoice = invoice_util.create_invoice(provider, child, today, due_date, enrollment.autopay_source_id, 0) # put a placeholder amount (0) for now, will calculate total amount after
                    invoice_dict[provider_child_pair_key] = invoice
                invoice_util.create_invoice_line_item(enrollment_key, invoice, program, due_date, cycle_end_date)
                # if should_add_registration_fee:
                #     invoice_util.create_invoice_line_item(enrollment_key, invoice, program, None, None, "Registration Fee", program.registrationFee)

    # Sum up total amount due
    for key in invoice_dict:
        invoice = invoice_dict[key]
        invoice.amount = invoice_util.sum_up_amount_due(invoice_dict[key])
        invoice.put()

    return HttpResponse(status=200)


def invoice_notification(request):
    logger.info("INVOICE NOTIFICATION")
    today = date.today()
    invoice_dict = dict()
    days_before = 5 # send notification 5 days before due date

    # loop over invoices...
    invoices = Invoice.query(Invoice.status != Invoice._POSSIBLE_STATUS['COMPLETED']).fetch()
    for invoice in invoices:
        logger.info("Sending notification for invoice: %s" % invoice)
        if today + timedelta(days=days_before) >= invoice.due_date and not invoice.email_sent:
            (start_date, end_date) = invoice_util.get_invoice_period(invoice)
            template = loader.get_template('invoice/invoice_invite.html')
            data = {
                'pay_invoice_url': request.get_host() + '/static/logo/img_headerbg.png',
                'invoice_id': invoice.key.id(),
                'start_date': start_date.strftime('%m/%d/%Y'),
                'end_date': end_date.strftime('%m/%d/%Y'),
                'due_date': invoice.due_date.strftime('%m/%d/%Y'),
                'school_name': invoice.provider_key.get().schoolName,
            }
            send_invoice_email(invoice.parent_email, invoice, start_date, end_date, template.render(data))
            invoice.email_sent = True
            invoice.put()
            break # temporary only sent out one email as our quota is limited

    return HttpResponse(status=200)

def autopay(request):
    logger.info("INVOICE AUTOPAY")
    #clear_webhook()
    #start_webhook()

    today = date.today()
    invoice_dict = dict()
    # loop over invoices...
    invoices = Invoice.query(Invoice.status != Invoice._POSSIBLE_STATUS['COMPLETED']).fetch()
    for invoice in invoices:
        (pay_days_before, autopay_source_id) = invoice_util.get_autopay_info(invoice)
        # if the invoice contains autopay data, and today is within the range, and the invoice is not paid
        if autopay_source_id and pay_days_before and today + timedelta(days=pay_days_before) >= invoice.due_date and not invoice.is_paid():
            logger.info("Autopaying for invoice: %s" % invoice)
            provider = invoice.provider_key.get()

            try:
                funding_util.make_transfer(provider.customerId, autopay_source_id, invoice.amount, invoice)
            except ValidationError as err:
                return HttpResponse(err.body['_embedded']['errors'][0]['message'])

            break # temporary only do one test autopay, remove before launch
        else:
            logger.info("Skipping autopay for invoice: %s" % invoice)

    return HttpResponse(status=200)

@csrf_exempt
def dwolla_webhook(request):
    logger.info("DWOLLA_WEBHOOK")
    webhook_content = json.loads(request.body)

    # webhook_content = {u'created': u'2017-04-26T04:04:27.831Z', u'resourceId': u'553c6c1f-0941-45dd-9038-2c9a32ce46ce',
    #                    u'topic': u'customer_funding_source_added', u'_links': {
    #         u'customer': {u'href': u'https://api-uat.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'},
    #         u'self': {u'href': u'https://api-uat.dwolla.com/events/88e0c745-0c2d-4441-a56b-b1c08382781c'},
    #         u'resource': {
    #             u'href': u'https://api-uat.dwolla.com/funding-sources/553c6c1f-0941-45dd-9038-2c9a32ce46ce'},
    #         u'account': {u'href': u'https://api-uat.dwolla.com/accounts/aaa5e130-ce8d-4807-82db-90961f7f1240'}},
    #                    u'timestamp': u'2017-04-26T04:04:27.831Z', u'id': u'88e0c745-0c2d-4441-a56b-b1c08382781c'}
    logger.info(webhook_content)
    webhook_data = parse_webhook_data(webhook_content)
    if DwollaEvent.get_by_id(webhook_data['id']) != None:
        logger.info("Webhook already processed.")
        return HttpResponse(status=200)
    host = request.get_host()
    if ('customer_transfer_created' in webhook_content['topic']):
        funded_transfer = get_funded_transfer(webhook_data['resource_url'])
        amount = funded_transfer['amount']
        parent = parent_util.get_parent_by_dwolla_id(funded_transfer['source_customer_url'])
        destination_customer_url = funded_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        source_funding_source = get_funding_source(funded_transfer['source_funding_url'])
        invoice = invoice_util.get_invoice_by_transfer_id(webhook_data['resource_url'])
        if invoice.status != Invoice._POSSIBLE_STATUS['PROCESSING']:
            invoice.status = Invoice._POSSIBLE_STATUS['PROCESSING']
            invoice.put()

        template = loader.get_template('funding/joobali-to-customer-transfer-created.html')
        data = {
            'transfer_type': 'Online',
            'amount': '$' + str(amount),
            'account_name': source_funding_source['name'],
            'recipient': provider.schoolName,
            'created_date': funded_transfer['created_date'],
            'host': host,
        }
        send_payment_created_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    elif ('customer_bank_transfer_completed' in webhook_data['topic']):
        funding_transfer = get_funding_transfer(webhook_data['resource_url'])
        funded_transfer = get_funded_transfer(funding_transfer['funded_transfer_url'])
        amount = funded_transfer['amount']
        parent = parent_util.get_parent_by_dwolla_id(funded_transfer['source_customer_url'])
        destination_customer_url = funded_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        source_funding_source = get_funding_source(funded_transfer['source_funding_url'])
        invoice = invoice_util.get_invoice_by_transfer_id(funding_transfer['funded_transfer_url'])
        if invoice.status != Invoice._POSSIBLE_STATUS['COMPLETED']:
            invoice.status = Invoice._POSSIBLE_STATUS['COMPLETED']
            invoice.put()

        template = loader.get_template('funding/joobali-to-customer-transfer-completed.html')
        data = {
            'transfer_type': 'Online',
            'amount': '$' + str(amount),
            'account_name': source_funding_source['name'],
            'recipient': provider.schoolName,
            'created_date': funded_transfer['created_date'],
            'host': host,
        }
        send_payment_success_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()

    elif ('customer_bank_transfer_cancelled' in webhook_data['topic']):
        funding_transfer = get_funding_transfer(webhook_data['resource_url'])
        funded_transfer = get_funded_transfer(funding_transfer['funded_transfer_url'])
        amount = funded_transfer['amount']
        parent = parent_util.get_parent_by_dwolla_id(funded_transfer['source_customer_url'])
        destination_customer_url = funded_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        source_funding_source = get_funding_source(funded_transfer['source_funding_url'])
        invoice = invoice_util.get_invoice_by_transfer_id(funding_transfer['funded_transfer_url'])
        if invoice.status != Invoice._POSSIBLE_STATUS['FAILED']:
            invoice.status = Invoice._POSSIBLE_STATUS['FAILED']
            invoice.put()

        template = loader.get_template('funding/joobali-to-customer-transfer-cancelled.html')
        data = {
            'transfer_type': 'Online',
            'amount': '$' + str(amount),
            'account_name': source_funding_source['name'],
            'recipient': provider.schoolName,
            'cancelled_date': webhook_data['event_date'],
            'host': host,
        }
        send_payment_cancelled_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        event = DwollaEvent(id=webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    elif ('customer_bank_transfer_failed' in webhook_data['topic']):
        funding_transfer = get_funding_transfer(webhook_data['resource_url'])
        funded_transfer = get_funded_transfer(funding_transfer['funded_transfer_url'])
        amount = funded_transfer['amount']
        parent = parent_util.get_parent_by_dwolla_id(funded_transfer['source_customer_url'])
        destination_customer_url = funded_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        invoice = invoice_util.get_invoice_by_transfer_id(funding_transfer['funded_transfer_url'])
        if invoice.status != Invoice._POSSIBLE_STATUS['FAILED']:
            invoice.status = Invoice._POSSIBLE_STATUS['FAILED']
            invoice.put()

        source_funding_source = get_funding_source(funded_transfer['source_funding_url'])
        template = loader.get_template('funding/joobali-to-customer-transfer-failed.html')
        data = {
            'transfer_type': 'Online',
            'amount': '$' + str(amount),
            'account_name': source_funding_source['name'],
            'recipient': provider.schoolName,
            'created_date': funded_transfer['created_date'],
            'host': host,
        }
        send_payment_failure_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    elif 'customer_funding_source_added' in webhook_data['topic']:
        funding_source = get_funding_source(webhook_data['resource_url'])
        first_name = None
        last_name = None
        email = None
        parent = parent_util.get_parent_by_dwolla_id(webhook_data['customer_url'])
        if not parent:
            provider = provider_util.get_provider_by_dwolla_id(webhook_data['customer_url'])
            first_name = provider.firstName
            last_name = provider.lastName
            email = provider.email
        else:
            first_name = parent.first_name
            last_name = parent.last_name
            email = parent.email

        template = loader.get_template('funding/joobali-to-customer-funding-source-added.html')
        data = {
            'bank_name': funding_source['bank_name'],
            'account_name': funding_source['name'],
            'created_date': funding_source['created_date'],
            'host': host,
        }
        send_funding_source_addition_email(email, first_name, funding_source['name'], template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()

    elif 'customer_funding_source_removed' in webhook_data['topic']:
        funding_source = get_funding_source(webhook_data['resource_url'])
        first_name = None
        last_name = None
        email = None
        parent = parent_util.get_parent_by_dwolla_id(webhook_data['customer_url'])
        if not parent:
            provider = provider_util.get_provider_by_dwolla_id(webhook_data['customer_url'])
            first_name = provider.firstName
            last_name = provider.lastName
            email = provider.email
        else:
            first_name = parent.first_name
            last_name = parent.last_name
            email = parent.email

        template = loader.get_template('funding/joobali-to-customer-funding-source-removed.html')
        data = {
            'bank_name': funding_source['bank_name'],
            'account_name': funding_source['name'],
            'removed_date': webhook_data['event_date'],
            'host': host,
        }
        send_funding_source_removal_email(email, first_name, funding_source['name'], template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    return HttpResponse(status=200)