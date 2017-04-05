from google.appengine.ext import ndb
from models import InvoiceLineItem
from models import Invoice
from common import key_util
from datetime import date, timedelta
from calendar import monthrange
import logging

logger = logging.getLogger(__name__)


def create_invoice_line_item(enrollment_key, invoice, program, start_date=None, end_date=None, description=None, amount=None):
    """Creates a new InvoiceLineItem"""
    invoice_line_item = InvoiceLineItem(parent=invoice.key)
    invoice_line_item.enrollment_key = enrollment_key
    invoice_line_item.invoice_key = invoice.key
    if amount:
        invoice_line_item.amount = amount
    else:
        invoice_line_item.amount = program.fee
    invoice_line_item.program_name = program.programName
    invoice_line_item.start_date = start_date
    invoice_line_item.end_date = end_date
    invoice_line_item.description = description
    invoice_line_item.put()
    return invoice_line_item

def create_invoice(provider, child, date, due_date, autopay_source_id=None, amount=None):
    """Creates a new Invoice"""
    id = "%s-%s-%s-%%s" % (provider.key.id(), child.key.id(), date)
    index = 1
    while Invoice.get_by_id(id % index):
        index += 1

    invoice = Invoice(id = id % index)
    invoice.provider_key = provider.key
    invoice.provider_email = provider.email
    invoice.provider_phone = provider.phone
    invoice.child_key = child.key
    invoice.child_first_name = child.first_name
    invoice.child_last_name = child.last_name
    invoice.parent_email = child.parent_email
    invoice.due_date = due_date
    invoice.date_created = date
    invoice.amount = amount
    invoice.autopay_source_id = autopay_source_id
    invoice.put()
    return invoice

def get_invoice_by_transfer_id(transfer_id):
    """ Gets a Invoice by the dwolla transfer id (must be funded_transfer because it's unique compared to funding_transfer """
    result = Invoice.query(Invoice.dwolla_transfer_id == transfer_id).fetch(1)
    if result:
        return result[0]
    return None

def sum_up_amount_due(invoice):
    """Sums up all the payment amount due for this invoice"""
    amount = 0
    # program related payment
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    for lineItem in lineItems:
        amount += lineItem.amount
    return amount

# def create_invoice_email(invoice):
#     """ Create the html email notification to customers"""
#     html = ''
#     lineItems = InvoiceLineItem.query(ancestor = invoice.key)
#     for lineItem in lineItems:
#         html += 'lineItem#:%s, %s, %s, %s' % (lineItem.program_name, lineItem.amount, lineItem.start_date, lineItem.end_date);
#     # adjustment payment
#     adjustments = InvoiceAdjustment.query(ancestor = invoice.key)
#     for adjustment in adjustments:
#         html += 'adjust#:%s, %s' % (adjustment.reason, adjustment.amount);
#     return html

def get_invoice_late_fee_added(invoice):
    """ Gets whether the late fee has been added to this unpaid late invoice. """
    today = date.today()
    if not invoice.is_paid() and invoice.due_date < today:
        lineItems = InvoiceLineItem.query(ancestor=invoice.key)
        for lineItem in lineItems:
            if lineItem.description == 'Late Fee':
                return True
    return False

def get_invoice_period(invoice):
    """ Gets the start and end date of current invoice billing period"""
    start_date = None
    end_date = None
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    for lineItem in lineItems:
        start_date = lineItem.start_date
        end_date = lineItem.end_date
        if start_date and end_date:
            break
    return (start_date, end_date)

def get_invoice_enrollment(invoice):
    """ Gets the first related enrollment of an invoice. None if their is no related enrollment. """
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    for lineItem in lineItems:
        if lineItem.enrollment_key and lineItem.enrollment_key.get():
            return lineItem.enrollment_key.get()
    return None

def get_invoice_program(invoice):
    """ Gets the first related program of an invoice. None if their is no related program. """
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    for lineItem in lineItems:
        if lineItem.enrollment_key and lineItem.enrollment_key.get() and lineItem.enrollment_key.get().program_key:
            return lineItem.enrollment_key.get().program_key.get()
    return None

def get_autopay_info(invoice):
    """ Gets the funding source id and the number of days before due date for autopayment from enrollment associated with this invoice"""
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    for lineItem in lineItems:
        enrollment = lineItem.enrollment_key.get()
        if enrollment:
            if enrollment.pay_days_before and enrollment.autopay_source_id:
                return (enrollment.pay_days_before, enrollment.autopay_source_id)
    return (None, None)

def get_invoice_enrollments(invoice):
    """ Gets all the enrollments contributing to the line items of this invoice"""
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    results = []
    for lineItem in lineItems:
        results.append(lineItem.enrollment_key.get())
    return results

def get_next_due_date(due_date, billing_freq):
    if billing_freq == 'Weekly':
        return due_date + timedelta(days=7)
    elif billing_freq == 'Monthly':
        return due_date + timedelta(days=monthrange(due_date.year, due_date.month)[1])
