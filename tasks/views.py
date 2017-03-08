from django.http import HttpResponse
from enrollment import enrollment_util
from invoice import invoice_util
from parent import parent_util
from login.models import Provider
from invoice.models import Invoice, InvoiceLineItem
from google.appengine.ext import ndb
from datetime import datetime, date
from datetime import timedelta
from common.email.invoice import send_invoice_email
from django.template import loader
from funding import funding_util
from dwollav2.error import ValidationError
from parent.models import Parent
import logging

logger = logging.getLogger(__name__)

def invoice_calculation(request):
    print "INVOICE CALCULATION"
    today = date.today()
    invoice_dict = dict() # a map from provider-child pair to invoice
    days_before = 5
    # loop over providers...
    providers = Provider.query().fetch()
    for provider in providers:
        logger.info("Calculating invoices for provider: %s" % provider)

        enrollments = enrollment_util.list_enrollment_by_provider(provider.key.id())
        for enrollment in enrollments:
            logger.info("Calculating invoice for enrollment: %s" % enrollment)

            child_key = enrollment["child_key"]
            program_key = enrollment["program_key"]
            child = child_key.get()
            program = program_key.get()
            cycle_start_date = program.startDate
            # using enrollment start date as due_date anchor,
            # which means if the start date is a Wednesday and the billing cycle is Weekly,
            # then the next invoice due date will be upcomming Wednesday.
            due_date = enrollment['start_date']

            should_proceed = False # whether we should generate a invoice for this enrollment now

            program_cycle_time = None # either a weekly cycle or a monthly cycle
            if program.billingFrequency == 'Weekly':
                program_cycle_time = timedelta(days=7)
            elif program.billingFrequency == 'Monthly':
                program_cycle_time = timedelta(months=1)
            else:
                logger.info("Skipping invoice calculation. Unexpected program cycle: %s" % program)
                should_proceed = False

            # find the upcomming due date in adding bill cycles to the enrollment start date until it passes today
            while due_date < today:
                due_date += program_cycle_time

            enrollment_key = ndb.Key("Provider", provider.key.id(), "Enrollment", enrollment["enrollment_id"])
            if due_date - timedelta(days=5) <= today: # 5 days ahead billing before due date
                should_proceed = True
                for invoice_line_item in InvoiceLineItem.query(InvoiceLineItem.enrollment_key == enrollment_key, InvoiceLineItem.start_date != None).fetch(): # line item without start date are adjustments
                    invoice = invoice_line_item.key.parent().get()
                    if invoice.due_date == due_date:
                        # if there is a existing invoice for this enrollment that have the same due date
                        # only proceed if current enrollment haven't yield a invoice for current billing cycle
                        logger.info("Skipping...Invoice has already been calculated for this cycle for enrollment: %s" % enrollment)
                        should_proceed = False



            # figure out the current cycle period, which is the program cycle period overlapping with current due date
            while cycle_start_date + program_cycle_time <= due_date:
                cycle_start_date += program_cycle_time

            if should_proceed:
                logger.info("Calculating Invoice: program: %s, child: %s" % (program, child))

                provider_child_pair_key = str(provider.key.id()) + str(child.key.id())
                invoice = None
                # for a single day, only generate one invoice per provider-child pair.
                # the single invoices can have multiple line items if the child enrolled in multiple programs.
                if provider_child_pair_key in invoice_dict:
                    invoice = invoice_dict[provider_child_pair_key]
                else:
                    invoice = invoice_util.create_invoice(provider, child, today, due_date, enrollment['autopay_source_id'], 0) # put a placeholder amount (0) for now, will calculate total amount after
                    invoice_dict[provider_child_pair_key] = invoice
                invoice_util.create_invoice_line_item(enrollment_key, invoice, program, cycle_start_date, cycle_start_date + program_cycle_time)

    # Sum up total amount due
    for key in invoice_dict:
        invoice = invoice_dict[key]
        invoice.amount = invoice_util.sum_up_amount_due(invoice_dict[key])
        invoice.put()

    return HttpResponse(status=200)


def invoice_notification(request):
    print "INVOICE NOTIFICATION"
    today = date.today()
    invoice_dict = dict()
    days_before = 5 # send notification 5 days before due date

    # loop over invoices...
    invoices = Invoice.query(Invoice.paid==False).fetch()
    for invoice in invoices:
        if today + timedelta(days=days_before) >= invoice.due_date and not invoice.email_sent:
            (start_date, end_date) = invoice_util.get_invoice_period(invoice)
            template = loader.get_template('invoice/invoice_invite.html')
            data = {
                'pay_invoice_url': 'http://joobali-1310.appspot.com/static/logo/img_headerbg.png',
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
    print "INVOICE AUTOPAY"
    today = date.today()
    invoice_dict = dict()
    # loop over invoices...
    invoices = Invoice.query(Invoice.paid==False).fetch()
    for invoice in invoices:
        (pay_days_before, contain_pay_days_before) = invoice_util.get_autopay_days_before(invoice)
        # if the invoice contains autopay data, and today is within the range, and the invoice is not paid
        if invoice.autopay_source_id and contain_pay_days_before and today + timedelta(days=pay_days_before) >= invoice.due_date and not invoice.paid:
            provider = invoice.provider_key.get()

            try:
                funding_util.make_transfer(provider.customerId, invoice.autopay_source_id, invoice.amount)
            except ValidationError as err:
                return HttpResponse(err.body['_embedded']['errors'][0]['message'])
            invoice.paid = True
            invoice.put()
            break # temporary only do one test autopay, remove before launch

    return HttpResponse(status=200)