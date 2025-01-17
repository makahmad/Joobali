from django.http import HttpResponse
from enrollment import enrollment_util
from enrollment.models import Enrollment
from invoice import invoice_util
from parent import parent_util
from login import provider_util
from login.models import Provider
from invoice.models import Invoice, InvoiceLineItem
from google.appengine.ext import ndb
from datetime import datetime, date
from datetime import timedelta
from common.dwolla import parse_webhook_data
from common.dwolla import get_bank_transfer, get_dwolla_transfer, get_funding_source
from common.email.invoice import send_invoice_email
from common.email.dwolla import send_funding_source_micro_deposits_completed_email, send_payment_cancelled_email_to_provider, send_payment_success_email_to_provider, send_payment_failed_email_to_provider, send_payment_success_email, send_payment_failed_email, send_funding_source_removal_email, send_funding_source_addition_email, send_payment_created_email, send_payment_created_email_to_provider, send_payment_cancelled_email
from common.dwolla import start_webhook, clear_webhook, client
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from funding import funding_util
from dwollav2.error import ValidationError
from models import DwollaEvent
from payments.models import Payment
from common import datetime_util
from common import dwolla
from common.request import get_host_from_request
from tasks.models import DwollaTokens
from funding.models import FeeRate
from funding import funding_util
from payments import payments_util
import logging
import json

logger = logging.getLogger(__name__)

DATE_FORMAT = '%m/%d/%Y'

def data_updating(request):
    for invoice in Invoice.query(Invoice.dwolla_transfer_id != None, Invoice.is_payment_cancellable == True).fetch():

        if invoice.is_processing():
            dwolla_transfer = get_dwolla_transfer(invoice.dwolla_transfer_id)
            if 'cancel' not in dwolla_transfer:
                invoice.is_payment_cancellable = False
                invoice.put()

    return HttpResponse(status=200)

def data_cleaning(request):
    for invoice_line_item in InvoiceLineItem.query().fetch():
        invoice = invoice_line_item.key.parent().get()
        if not invoice:
            logger.info("Deleting dangling invoice line item: %s" % invoice_line_item)
            invoice_line_item.key.delete()
    return HttpResponse(status=200)

def process_fee(request):
    now = datetime.now()

    providers = Provider.query().fetch()
    for provider in providers:
        if provider.time_created:
            if provider.time_created + timedelta(days=360) > now:
                rate = funding_util.get_fee_rate(provider.key.id())
                if not rate:
                    fee_rate = FeeRate()
                    fee_rate.provider_key = provider.key
                    fee_rate.rate = 0.01 # 1% for everyone
                    fee_rate.put()

    return HttpResponse(status=200)


def invoice_calculation(request):
    now = datetime.now()

    logger.info("LATE FEE CALCULATION")
    # loop over invoices...
    for invoice in Invoice.query().fetch():
        if not invoice.is_deleted(): # ignore deleted invoices
            provider = invoice.provider_key.get()
            if invoice.late_fee_enforced and not invoice.is_paid() and invoice.is_over_due(provider.graceDays if provider.graceDays >= 0 else 0) and not invoice_util.get_invoice_late_fee_added(invoice):
                logger.info("Considering late fee for invoice: %s" % invoice)
                program = invoice_util.get_invoice_program(invoice)
                enrollment = invoice_util.get_invoice_enrollment(invoice)
                provider = provider_util.get_provider_by_email(invoice.provider_email)
                lateFee = program.lateFee if program and program.lateFee else provider.lateFee
                if lateFee != 0:
                    logger.info("Adding late fee with program: %s" % program)
                    invoice_util.create_invoice_line_item(enrollment.key if enrollment else None, invoice, program, None, None, "Late Fee", lateFee)

                invoice.amount = invoice_util.sum_up_amount_due(invoice)
                invoice.put()

    logger.info("PAYMENT CALCULATION")
    # loop over invoices...
    query = Invoice.query().order(Invoice.time_created)
    for invoice in query.fetch():
        if not invoice.is_deleted(): # ignore deleted invoices
            if not invoice.is_paid() and not invoice.is_processing():
                logger.info("Considering payment for invoice: %s" % invoice)
                for payment in Payment.query(Payment.child_key==invoice.child_key, Payment.is_deleted==False).fetch():
                    if not payment.invoice_key or payment.invoice_key and payment.invoice_key == invoice.key:
                        if payment.balance > 0:
                            logger.info("Making payment with: %s" % payment)
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
            if enrollment.status == 'inactive' or enrollment.status == 'cancel':
                logger.info("Enrollment %s. Skipping calculation for enrollment: %s" % (enrollment.status, enrollment))
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
            while due_date < now:
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

            if due_date - timedelta(days=5) <= now: # 5 days ahead billing before due date
                should_proceed = True
                for invoice_line_item in InvoiceLineItem.query(InvoiceLineItem.enrollment_key == enrollment.key, InvoiceLineItem.start_date != None).fetch(): # line item without start date are adjustments
                    invoice = invoice_line_item.key.parent().get()
                    # Note: This can be a deleted invoice, if a auto-created invoice is deleted, we will not create it again.
                    if invoice and invoice.due_date == due_date:
                        # if there is a existing invoice for this enrollment that have the same due date
                        # only proceed if current enrollment haven't yield a invoice for current billing cycle
                        logger.info("Skipping...Invoice has already been calculated for this cycle for enrollment: %s" % enrollment)
                        should_proceed = False
            else:
                logger.info("Skipping, due date too far away: today - %s, due date - %s" % (now, due_date))

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
                # NOTE: disable this for launch. One invoice for each program of the child.
                try:
                    if False: # provider_child_pair_key in invoice_dict:
                        invoice = invoice_dict[provider_child_pair_key]
                    else:
                        invoice = invoice_util.create_invoice(provider, child, due_date, enrollment.autopay_source_id, 0) # put a placeholder amount (0) for now, will calculate total amount after
                        logger.info("INVOICE CREATED: %s" % invoice)
                        invoice.is_recurring = True
                        #invoice_dict[provider_child_pair_key] = invoice
                        invoice_dict[invoice.key.id()] = invoice
                    invoice_line_item = invoice_util.create_invoice_line_item(enrollment.key, invoice, program, due_date, cycle_end_date)
                    logger.info("INVOICE LINE ITEM CREATED: %s" % invoice_line_item)
                except Exception as e:
                    logger.error(e)
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

    # loop over invoices...
    invoices = Invoice.query(Invoice.status != Invoice._POSSIBLE_STATUS['COMPLETED']).fetch()
    for invoice in invoices:
        if not invoice.is_deleted(): # ignore deleted invoices
            if invoice.send_email and not invoice.email_sent and invoice.amount > 0:
                enrollment = invoice_util.get_invoice_enrollment(invoice)
                if enrollment and not enrollment.is_active():
                    logger.info("Enrollment not active - Skipping notification for invoice: %s" % invoice)
                    continue
                logger.info("Sending notification for invoice: %s" % invoice)
                (start_date, end_date) = invoice_util.get_invoice_period(invoice)
                program = None
                if enrollment:
                    program = enrollment.program_key.get()
                parent = parent_util.get_parents_by_email(invoice.parent_email)
                template = loader.get_template('invoice/invoice_reminder.html')
                data = {
                    'autopay_setup': True if invoice.autopay_source_id else False,
                    'is_recurring': invoice.is_recurring,
                    'host': get_host_from_request(request.get_host()),
                    'invoice_id': invoice.key.id(),
                    'start_date': datetime_util.utc_to_local(start_date).strftime('%m/%d/%Y') if start_date else '',
                    'end_date': datetime_util.utc_to_local(end_date).strftime('%m/%d/%Y') if end_date else '',
                    'due_date': datetime_util.utc_to_local(invoice.due_date).strftime('%m/%d/%Y'),
                    'school_name': invoice.provider_key.get().schoolName,
                    'program_name': program.programName if program else '',
                    'program_billing_frequency': program.billingFrequency if program else '',
                    'amount': invoice.amount,
                    'parent_name': parent.first_name if parent else '',
                    'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
                }
                send_invoice_email(invoice.parent_email, invoice, datetime_util.utc_to_local(start_date), datetime_util.utc_to_local(end_date), template.render(data))
                invoice.email_sent = True
                invoice.put()
                # break # temporary only sent out one email as our quota is limited

    return HttpResponse(status=200)

def autopay(request):
    logger.info("INVOICE AUTOPAY")

    now = datetime.now()
    invoice_dict = dict()
    # loop over invoices...
    invoices = Invoice.query(Invoice.status != Invoice._POSSIBLE_STATUS['COMPLETED']).fetch()
    for invoice in invoices:
        if not invoice.is_deleted(): # ignore deleted invoices
            (pay_days_before, autopay_source_id) = invoice_util.get_autopay_info(invoice)
            pay_days_before = 0 if pay_days_before == None else pay_days_before
            # if the invoice contains autopay data, and today is within the range, and the invoice is not paid
            if autopay_source_id != None and pay_days_before != None and now + timedelta(days=pay_days_before) >= invoice.due_date - timedelta(days=1) and not invoice.is_paid() and not invoice.is_processing():
                logger.info("Autopaying for invoice: %s" % invoice)
                provider = invoice.provider_key.get()
                rate = funding_util.get_fee_rate(provider.key.id())
                try:
                    funding_util.make_transfer(provider.customerId, autopay_source_id, invoice.amount, invoice, rate)
                except ValidationError as err:
                    logger.info("Autopay failed: %s" % err.body['_embedded']['errors'][0]['message'])

                    invoice.autopay_failure_message = err.body['_embedded']['errors'][0]['message']
                    invoice.status = Invoice._POSSIBLE_STATUS['FAILED']
                    invoice.put()
                    logger.error(err.body['_embedded']['errors'][0]['message'])
                except Exception as e:
                    logger.error(e)
            else:
                logger.info("Skipping autopay (autopay_source_id: %s; pay_days_before: %s; now: %s) for invoice: %s" % (autopay_source_id, pay_days_before, invoice, now))

    return HttpResponse(status=200)

def dwolla_webhook_setup(request):
    logger.info("DWOLLA WEBHOOK SETUP")
    clear_webhook(request.get_host())
    start_webhook('%s://%s' % (request.scheme, request.get_host()))
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
    # When the money stays in dwolla balance.
    # {
    #     u'created': u'2017-06-05T03:32:03.943   Z',
    #     u'resourceId': u'71649077-5c49-e711-80f2-0aa34a9b2388',
    #     u'topic': u'customer_transfer_completed',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api-sandbox.dwolla.com/customers/441b7124-12a0-4d76-a9af-48ef513408cc'
    #         },
    #         u'self': {
    #             u'href': u'https://api-sandbox.dwolla.com/events/3c2e2daa-8fe3-4b81-9ca4-e964ae4186b3'
    #         },
    #         u'resource': {
    #             u'href': u'https://api-sandbox.dwolla.com/transfers/71649077-5c49-e711-80f2-0aa34a9b2388'
    #         },
    #         u'account': {
    #             u'href': u'https://api-sandbox.dwolla.com/accounts/aaa5e130-ce8d-4807-82db-90961f7f1240'
    #         }
    #     },
    #     u'timestamp': u'2017-06-05T03:32:03.943   Z',
    #     u'id': u'3c2e2daa-8fe3-4b81-9ca4-e964ae4186b3'
    # }
    # Another example:
    # {
    #     u'created': u'2017-08-10T14:00:56.058   Z',
    #     u'resourceId': u'f20aa389-8223-41ae-b796-fd4f64e3c410',
    #     u'topic': u'customer_microdeposits_completed',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api.dwolla.com/customers/56e1b292-2d6c-4df3-a6ee-c97adff481d7'
    #         },
    #         u'self': {
    #             u'href': u'https://api.dwolla.com/events/d697cf3a-07f1-48c8-8152-48ced5d613dd'
    #         },
    #         u'resource': {
    #             u'href': u'https://api.dwolla.com/funding-sources/f20aa389-8223-41ae-b796-fd4f64e3c410'
    #         },
    #         u'account': {
    #             u'href': u'https://api.dwolla.com/accounts/6d081097-35f7-4119-9c4e-530d35de2711'
    #         }
    #     },
    #     u'timestamp': u'2017-08-10T14:00:56.058   Z',
    #     u'id': u'd697cf3a-07f1-48c8-8152-48ced5d613dd'
    # }
    logger.info(webhook_content)
    webhook_data = parse_webhook_data(webhook_content)
    if DwollaEvent.get_by_id(webhook_data['id']) != None:
        logger.info("Webhook already processed.")
        return HttpResponse(status=200)
    host = get_host_from_request(request.get_host())
    support_phone = '301-538-6558'
    if ('customer_transfer_created' in webhook_content['topic']):
        dwolla_transfer = get_dwolla_transfer(webhook_data['resource_url'])
        amount = dwolla_transfer['amount']
        source_customer_url = dwolla_transfer['source_customer_url']
        parent = parent_util.get_parent_by_dwolla_id(source_customer_url)
        destination_customer_url = dwolla_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        customer_url = webhook_data['customer_url']

        to_provider = False
        to_parent = False
        if customer_url == destination_customer_url:
            to_provider = True
        if customer_url == source_customer_url:
            to_parent = True

        source_funding_source = get_funding_source(dwolla_transfer['source_funding_url'])
        invoice = invoice_util.get_invoice_by_transfer_id(webhook_data['resource_url'])
        if invoice.status != Invoice._POSSIBLE_STATUS['PROCESSING']:
            invoice.status = Invoice._POSSIBLE_STATUS['PROCESSING']
            invoice.put()

        if to_parent:
            template = loader.get_template('funding/joobali-to-customer-transfer-created.html')
            data = {
                'invoice_id': invoice.key.id() if invoice else '',
                'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
                'first_name': parent.first_name if parent.first_name else '',
                'transfer_type': 'Online',
                'amount': str(amount),
                'account_name': source_funding_source['name'],
                'recipient': provider.schoolName,
                'created_date': dwolla_transfer['created_date'],
                'host': host,
                'support_phone': support_phone
            }
            send_payment_created_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        if to_provider:
            destination_funding_source = get_funding_source(dwolla_transfer['destination_funding_url'])
            template = loader.get_template('funding/joobali-to-provider-transfer-created.html')
            data = {
                'invoice_id': invoice.key.id() if invoice else '',
                'first_name': provider.firstName if provider.firstName else '',
                'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
                'transfer_type': 'Online',
                'amount': str(amount),
                'account_name': destination_funding_source['name'],
                'sender': '%s %s' % (parent.first_name, parent.last_name),
                'created_date': dwolla_transfer['created_date'],
                'host': host,
                'support_phone': support_phone
            }
            send_payment_created_email_to_provider(provider.email, provider.firstName, '%s %s' % (parent.first_name, parent.last_name), provider.schoolName, amount, template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    elif ('customer_bank_transfer_completed' in webhook_data['topic']):
        bank_transfer = get_bank_transfer(webhook_data['resource_url'])
        dwolla_transfer_url = bank_transfer['funding_transfer_url'] if bank_transfer['funding_transfer_url'] else bank_transfer['funded_transfer_url']
        dwolla_transfer = get_dwolla_transfer(dwolla_transfer_url)
        amount = dwolla_transfer['amount']
        source_customer_url = dwolla_transfer['source_customer_url']
        parent = parent_util.get_parent_by_dwolla_id(source_customer_url)
        destination_customer_url = dwolla_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        customer_url = webhook_data['customer_url']

        to_provider = False
        to_parent = False
        if customer_url == destination_customer_url:
            to_provider = True
        if customer_url == source_customer_url:
            to_parent = True

        source_funding_source = get_funding_source(dwolla_transfer['source_funding_url'])
        invoice = invoice_util.get_invoice_by_transfer_id(dwolla_transfer_url)
        if invoice.status != Invoice._POSSIBLE_STATUS['COMPLETED']:
            invoice.status = Invoice._POSSIBLE_STATUS['COMPLETED']
            invoice.amount = 0
            invoice.put()

        if to_parent:
            template = loader.get_template('funding/joobali-to-customer-transfer-completed.html')
            data = {
                'invoice_id': invoice.key.id() if invoice else '',
                'transfer_type': 'Online',
                'amount': str(amount),
                'account_name': source_funding_source['name'],
                'recipient': provider.schoolName,
                'created_date': dwolla_transfer['created_date'],
                'host': host,
                'support_phone': support_phone,
                'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),

                'date_paid': datetime_util.utc_to_local(invoice.time_updated).strftime(
                    '%m/%d/%Y') if invoice.time_updated else '',
                'invoice_description': invoice_util.get_invoice_snippet(invoice),

                'first_name': parent.first_name if parent.first_name else '',
                'provider_street': provider.addressLine1 + (
                    ", %s" % provider.addressLine2) if provider.addressLine2 else provider.addressLine1,
                'provider_city_state_zipcode': '%s, %s, %s' % (provider.city, provider.state, provider.zipcode) if provider.city and provider.state and provider.zipcode else None,
                'provider_name': provider.schoolName,
                'provider_phone': provider.phone if provider.phone else None,
                'parent_name': '%s %s' % (parent.first_name, parent.last_name),
                'provider_tin': provider.tin if provider.tin else None,
            }
            send_payment_success_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        if to_provider:
            destination_funding_source = get_funding_source(dwolla_transfer['destination_funding_url'])
            template = loader.get_template('funding/joobali-to-provider-transfer-completed.html')
            data = {
                'invoice_id': invoice.key.id() if invoice else '',
                'first_name': provider.firstName if provider.firstName else '',
                'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
                'transfer_type': 'Online',
                'amount': str(amount),
                'account_name': destination_funding_source['name'],
                'sender': '%s %s' % (parent.first_name, parent.last_name),
                'created_date': dwolla_transfer['created_date'],
                'host': host,
                'support_phone': support_phone
            }
            send_payment_success_email_to_provider(provider.email, provider.firstName, '%s %s' % (parent.first_name, parent.last_name), provider.schoolName, amount, template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()

    elif ('customer_bank_transfer_cancelled' in webhook_data['topic']):
        bank_transfer = get_bank_transfer(webhook_data['resource_url'])
        dwolla_transfer_url = bank_transfer['funding_transfer_url'] if bank_transfer['funding_transfer_url'] else bank_transfer['funded_transfer_url']
        dwolla_transfer = get_dwolla_transfer(dwolla_transfer_url)
        amount = dwolla_transfer['amount']
        parent = parent_util.get_parent_by_dwolla_id(dwolla_transfer['source_customer_url'])
        destination_customer_url = dwolla_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        source_funding_source = get_funding_source(dwolla_transfer['source_funding_url'])
        invoice = invoice_util.get_invoice_by_transfer_id(dwolla_transfer_url)

        if invoice.status != Invoice._POSSIBLE_STATUS['CANCELLED']:
            invoice.status = Invoice._POSSIBLE_STATUS['CANCELLED']
            # invoice.cancelled_transfer_ids.append(invoice.dwolla_transfer_id)
            invoice.dwolla_transfer_id = None
            invoice.put()

        for payment in Payment.query(Payment.invoice_key == invoice.key).fetch():
            if payment.type == 'Online Transfer' and payment.dwolla_transfer_id == invoice.dwolla_transfer_id:
                payment.status = dwolla_transfer['status']
                payment.put()

        template = loader.get_template('funding/joobali-to-customer-transfer-cancelled.html')
        data = {
            'invoice_id': invoice.key.id() if invoice else '',
            'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
            'first_name': parent.first_name if parent.first_name else '',
            'transfer_type': 'Online',
            'amount': str(amount),
            'account_name': source_funding_source['name'],
            'recipient': provider.schoolName,
            'created_date': dwolla_transfer['created_date'],
            'host': host,
            'support_phone': support_phone
        }
        send_payment_cancelled_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        destination_funding_source = get_funding_source(dwolla_transfer['destination_funding_url'])
        template = loader.get_template('funding/joobali-to-provider-transfer-cancelled.html')
        data = {
            'invoice_id': invoice.key.id() if invoice else '',
            'first_name': provider.firstName if provider.firstName else '',
            'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
            'transfer_type': 'Online',
            'amount': str(amount),
            'account_name': destination_funding_source['name'],
            'sender': '%s %s' % (parent.first_name, parent.last_name),
            'created_date': dwolla_transfer['created_date'],
            'host': host,
            'support_phone': support_phone
        }
        send_payment_cancelled_email_to_provider(provider.email, provider.firstName, '%s %s' % (parent.first_name, parent.last_name), provider.schoolName, amount, template.render(data))

        event = DwollaEvent(id=webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    elif ('customer_bank_transfer_failed' in webhook_data['topic']):
        bank_transfer = get_bank_transfer(webhook_data['resource_url'])
        dwolla_transfer_url = bank_transfer['funding_transfer_url'] if bank_transfer['funding_transfer_url'] else bank_transfer['funded_transfer_url']
        dwolla_transfer = get_dwolla_transfer(dwolla_transfer_url)
        amount = dwolla_transfer['amount']
        parent = parent_util.get_parent_by_dwolla_id(dwolla_transfer['source_customer_url'])
        destination_customer_url = dwolla_transfer['destination_customer_url']
        provider = provider_util.get_provider_by_dwolla_id(destination_customer_url)

        invoice = invoice_util.get_invoice_by_transfer_id(dwolla_transfer_url)
        if invoice.status != Invoice._POSSIBLE_STATUS['FAILED']:
            invoice.status = Invoice._POSSIBLE_STATUS['FAILED']
            invoice.put()

        for payment in Payment.query(Payment.invoice_key == invoice.key).fetch():
            if payment.type == 'Online Transfer' and payment.dwolla_transfer_id == invoice.dwolla_transfer_id:
                payment.status = dwolla_transfer['status']
                payment.put()

        source_funding_source = get_funding_source(dwolla_transfer['source_funding_url'])
        template = loader.get_template('funding/joobali-to-customer-transfer-failed.html')
        data = {
            'invoice_id': invoice.key.id() if invoice else '',
            'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
            'first_name': parent.first_name if parent.first_name else '',
            'transfer_type': 'Online',
            'amount': str(amount),
            'account_name': source_funding_source['name'],
            'recipient': provider.schoolName,
            'created_date': dwolla_transfer['created_date'],
            'host': host,
            'support_phone': support_phone
        }
        send_payment_failed_email(parent.email, parent.first_name, provider.schoolName, amount, template.render(data))

        destination_funding_source = get_funding_source(dwolla_transfer['destination_funding_url'])
        template = loader.get_template('funding/joobali-to-provider-transfer-failed.html')
        data = {
            'invoice_id': invoice.key.id() if invoice else '',
            'first_name': provider.firstName if provider.firstName else '',
            'child_name': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
            'transfer_type': 'Online',
            'amount': str(amount),
            'account_name': destination_funding_source['name'],
            'sender': '%s %s' % (parent.first_name, parent.last_name),
            'created_date': dwolla_transfer['created_date'],
            'host': host,
            'support_phone': support_phone
        }
        send_payment_failed_email_to_provider(provider.email, provider.firstName, '%s %s' % (parent.first_name, parent.last_name), provider.schoolName, amount, template.render(data))

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
            'first_name': first_name,
            'bank_name': funding_source['bank_name'],
            'account_name': funding_source['name'],
            'created_date': funding_source['created_date'],
            'host': host,
            'support_phone': support_phone
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
            'first_name': first_name,
            'bank_name': funding_source['bank_name'],
            'account_name': funding_source['name'],
            'removed_date': webhook_data['event_date'],
            'host': host,
            'support_phone': support_phone
        }
        send_funding_source_removal_email(email, first_name, funding_source['name'], template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    elif 'customer_microdeposits_completed' in webhook_data['topic']:
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

        template = loader.get_template('funding/joobali-to-customer-funding-source-micro-deposits-completed.html')
        data = {
            'first_name': first_name,
            'bank_name': funding_source['bank_name'],
            'account_name': funding_source['name'],
            'host': host,
            'support_phone': support_phone
        }
        send_funding_source_micro_deposits_completed_email(email, first_name, funding_source['name'], template.render(data))

        event = DwollaEvent(id = webhook_data['id'])
        event.event_id = webhook_data['id']
        event.event_content = str(webhook_content)
        event.put()
    return HttpResponse(status=200)

def dwolla_token_refresh(request):
    logger.info("DWOLLA TOKEN REFRESH")

    application_token = client.Auth.client()
    logger.info(application_token.access_token)
    logger.info(application_token.expires_in)

    tokens = DwollaTokens.query().fetch(1)
    if not tokens:
        tokens = DwollaTokens()
        tokens.access_token = application_token.access_token
        tokens.refresh_token = application_token.refresh_token if application_token.refresh_token else ''
        tokens.put()
        pass # token empty. Page on call!!
    else:
        tokens[0].access_token = application_token.access_token
        tokens[0].put()
    return HttpResponse(status=200)


def enrollment_status_update_by_time_passage(request):
    logger.info("Updating enrollment from active to inactive passing the enrollment end date")
    current_date = datetime.utcnow()
    enrollments = Enrollment.query(Enrollment.status == 'active', Enrollment.end_date <= current_date)
    for enrollment in enrollments:
        logger.info(enrollment)
        enrollment.status = 'inactive'
        enrollment.put()
    return HttpResponse(status=200)
