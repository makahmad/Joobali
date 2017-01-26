from django.http import HttpResponse
from enrollment import enrollment_util
from invoice import invoice_util
from parent import parent_util
from login.models import Provider
from invoice.models import Invoice
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
    print today
    invoice_dict = dict()
    days_before = 5
    # loop over providers...
    providers = Provider.query().fetch()
    for provider in providers:
        print provider
        enrollments = enrollment_util.list_enrollment_by_provider(provider.key.id())
        for enrollment in enrollments:
            print enrollment
            child_key = enrollment["child_key"]
            program_key = enrollment["program_key"]
            child = child_key.get()
            program = program_key.get()
            cycle_start_date = program.startDate
            due_date = enrollment['start_date']

            should_proceed = False
            program_cycle_time = None
            if program.billingFrequency == 'Weekly':
                program_cycle_time = timedelta(days=7)
            elif program.billingFrequency == 'Monthly':
                program_cycle_time = timedelta(months=1)
            else:
                logger.info("Skipping invoice calculation (unexpected frequency): program: %s" % program)
                should_proceed = False

            logger.info("Calculating Invoice: program: %s, child: %s" % (program, child))
            while due_date < today:
                due_date += program_cycle_time
            logger.info("Calculating Invoice: due_date: %s, today: %s" % (due_date, today))
            if due_date - timedelta(days=5) <= today: # 5 days ahead billing before due date
                should_proceed = True
            while cycle_start_date + timedelta(days=days_before) < due_date:
                cycle_start_date += program_cycle_time
            if should_proceed:
                logger.info("Calculating Invoice: program: %s, child: %s" % (program, child))

                provider_child_pair_key = provider.key.id() + str(child.key.id())
                invoice = None
                if provider_child_pair_key in invoice_dict:
                    invoice = invoice_dict[provider_child_pair_key]
                else:
                    invoice = invoice_util.create_invoice(provider, child, today, due_date)
                    invoice_dict[provider_child_pair_key] = invoice
                invoice_util.create_invoice_line_item(ndb.Key("Enrollment", enrollment["enrollment_id"]), invoice, program, cycle_start_date, cycle_start_date + program_cycle_time)

    # Sum up total amount due
    for key in invoice_dict:
        invoice = invoice_dict[key]
        invoice.amount = invoice_util.sum_up_amount_due(invoice_dict[key])
        invoice.put()

    return HttpResponse(status=200)


def invoice_notification(request):
    print "INVOICE NOTIFICATION"
    today = date.today()
    print today
    invoice_dict = dict()
    days_before = 5
    # loop over invoices...
    invoices = Invoice.query(Invoice.paid==False).fetch()
    for invoice in invoices:
        if today + timedelta(days=days_before) >= invoice.due_date and not invoice.email_sent:
            (start_date, end_date) = invoice_util.get_invoice_period(invoice)
            template = loader.get_template('invoice/invoice_invite.html')
            data = {
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
    print today
    invoice_dict = dict()
    days_before = 5
    # loop over invoices...
    invoices = Invoice.query(Invoice.paid==False).fetch()
    for invoice in invoices:
        if today + timedelta(days=days_before) >= invoice.due_date and not invoice.paid:
            provider = invoice.provider_key.get()
            parent = Parent.get_by_id(invoice.parent_email)
            # autopay_source_id = '593b86cd-7f6a-418e-8fce-61fa7d173b7b'

            try:
                funding_util.make_transfer(provider.customerId, invoice.autopay_source_id, invoice.amount)
            except ValidationError as err:
                return HttpResponse(err.body['_embedded']['errors'][0]['message'])
            invoice.paid = True
            invoice.put()
            break # temporary only do one test autopay

    return HttpResponse(status=200)