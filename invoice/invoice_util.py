from google.appengine.ext import ndb
from models import InvoiceAdjustment
from models import InvoiceLineItem
from models import Invoice
from common import key_util
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_invoice_line_item(enrollment_key, invoice, program, start_date, end_date):
    """Creates a new InvoiceLineItem"""
    invoice_line_item = InvoiceLineItem(parent=invoice.key)
    invoice_line_item.enrollment_key = enrollment_key
    invoice_line_item.invoice_key = invoice.key
    invoice_line_item.amount = program.fee
    invoice_line_item.program_name = program.programName
    invoice_line_item.start_date = start_date
    invoice_line_item.end_date = end_date
    invoice_line_item.put()
    return invoice_line_item

def create_invoice(provider, child, date, due_date):
    """Creates a new Invoice"""
    invoice = Invoice(id = "%s-%s-%s" % (provider.key.id(), child.key.id(), date))
    invoice.provider_key = provider.key
    invoice.provider_email = provider.email
    invoice.provider_phone = provider.phone
    invoice.child_key = child.key
    invoice.child_first_name = child.first_name
    invoice.child_last_name = child.last_name
    invoice.parent_email = child.parent_email
    invoice.due_date = due_date
    invoice.date_created = date
    invoice.amount = 0
    invoice.put()
    return invoice

def sum_up_amount_due(invoice):
    """Sums up all the payment amount due for this invoice"""
    amount = 0
    # program related payment
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    for lineItem in lineItems:
        amount += lineItem.amount
    # adjustment payment
    adjustments = InvoiceAdjustment.query(ancestor = invoice.key)
    for adjustment in adjustments:
        amount += adjustment.amount
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

def get_invoice_period(invoice):
    """ Gets the start and end date of current invoice billing period"""
    start_date = None
    end_date = None
    lineItems = InvoiceLineItem.query(ancestor = invoice.key)
    for lineItem in lineItems:
        start_date = lineItem.start_date
        end_date = lineItem.end_date
        break
    return (start_date, end_date)