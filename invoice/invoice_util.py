from google.appengine.ext import ndb
from models import InvoiceLineItem
from models import Invoice
from common import key_util
from datetime import datetime, date, timedelta
from calendar import monthrange
from common import datetime_util
import logging

logger = logging.getLogger(__name__)


def create_invoice_line_item(enrollment_key, invoice, program, start_date=None, end_date=None, description=None, amount=None, payment=None):
    """Creates a new InvoiceLineItem"""
    invoice_line_item = InvoiceLineItem(parent=invoice.key)
    invoice_line_item.enrollment_key = enrollment_key
    invoice_line_item.invoice_key = invoice.key
    if amount is not None and amount != 0:
        invoice_line_item.amount = amount
    else:
        invoice_line_item.amount = program.fee if program else 0.0
    invoice_line_item.program_name = program.programName if program else ''
    invoice_line_item.start_date = start_date
    invoice_line_item.end_date = end_date
    invoice_line_item.description = description
    if payment:
        invoice_line_item.payment_key = payment.key
    invoice_line_item.put()
    return invoice_line_item

def create_invoice(provider, child, due_date, autopay_source_id=None, amount=None, late_fee_enforced=True):
    """Creates a new Invoice"""
    id = "%s-%s-%s-%%s" % (provider.key.id(), child.key.id(), datetime_util.utc_to_local(datetime.now()).strftime("%m%d%Y"))
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
    invoice.amount = amount
    invoice.autopay_source_id = autopay_source_id
    invoice.late_fee_enforced = late_fee_enforced
    invoice.general_note = provider.generalInvoiceNote
    invoice.late_fee_note = provider.lateFeeInvoiceNote
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

def sum_up_original_amount_due(invoice):
    """Sums up all the payment amount due for this invoice except payment line items"""
    amount = 0
    # program related payment
    lineItems = InvoiceLineItem.query(ancestor = invoice.key).filter(InvoiceLineItem.payment_key == None)
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
    now = datetime.now()
    if not invoice.is_paid() and invoice.due_date < now:
        lineItems = InvoiceLineItem.query(ancestor=invoice.key)
        for lineItem in lineItems:
            if lineItem.description == 'Late Fee':
                return True
    return False

def get_invoice_snippet(invoice):
    """ Gets a brief description of what the invoice involves """
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    program = get_invoice_program(invoice)
    if program:
        return program.programName
    for lineItem in lineItems:
        if 'Registration' in lineItem.description:
            return lineItem.description
    return ''

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
        if lineItem.enrollment_key:
            enrollment = lineItem.enrollment_key.get()
            if enrollment:
                if enrollment.pay_days_before != None and enrollment.autopay_source_id != None:
                    return (enrollment.pay_days_before, enrollment.autopay_source_id)
    return (None, None)

def get_invoice_enrollments(invoice):
    """ Gets all unique enrollments contributing to the line items of this invoice"""
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    results = []
    ids = dict()
    for lineItem in lineItems:
        if lineItem.enrollment_key and lineItem.enrollment_key.get() and lineItem.enrollment_key.id not in ids:
            ids[lineItem.enrollment_key.id] = True
            results.append(lineItem.enrollment_key.get())
    return results

def get_enrollment_invoices(enrollment):
    """ Gets all the invoices related to the given enrollments"""
    lineItems = InvoiceLineItem.query(InvoiceLineItem.enrollment_key == enrollment.key)
    results = []
    for lineItem in lineItems:
        results.append(lineItem.key.parent().get())
    return results

def get_next_due_date(due_date, billing_freq):
    if billing_freq == 'Weekly':
        return due_date + timedelta(days=7)
    elif billing_freq == 'Monthly':
        next_month_day = due_date.day
        current_month_days_left = monthrange(due_date.year, due_date.month)[1] - due_date.day
        if due_date.day > 28: # last day of the month
            month = 1 if due_date.month == 12 else due_date.month + 1
            year = due_date.year + 1 if due_date.month == 12 else due_date.year
            next_month_day = monthrange(year, month)[1]

        return due_date + timedelta(days=current_month_days_left) + timedelta(days=next_month_day)

def list_invoice_by_provider_and_child(provider_key, child_key):
    invoice_query = Invoice.query(Invoice.child_key == child_key, Invoice.provider_key == provider_key)
    invoices = list()
    for invoice in invoice_query:
        invoices.append(invoice)
    return invoices


@ndb.transactional(xg=True)
def pay(invoice, payment):
    if payment.balance >= invoice.amount:
        amount = invoice.amount
        create_invoice_line_item(None, invoice, None, None, None, "Payment from %s" % payment.payer,
                                              -amount, payment)
        payment.balance = payment.balance - invoice.amount
        invoice.status = Invoice._POSSIBLE_STATUS['PAID_OFFLINE']
        invoice.amount = 0
        payment.put()
        invoice.put()
    else:
        amount = payment.balance
        create_invoice_line_item(None, invoice, None, None, None, "Payment from %s" % payment.payer,
                                              -amount, payment)
        invoice.amount = invoice.amount - payment.balance
        payment.balance = 0
        payment.put()
        invoice.put()


@ndb.transactional(xg=True)
def adjust_invoice(invoice, amount, reason):
    create_invoice_line_item(None, invoice, None, None, None, reason,
                                          -amount, None)
    invoice.amount = invoice.amount - amount
    invoice.put()