from google.appengine.ext import ndb
from models import InvoiceLineItem
from models import Invoice
from common import key_util
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_invoice_line_item(enrollment_key, invoice_key):
    """Creates a new InvoiceLineItem"""
    invoice_line_item = InvoiceLineItem()
    invoice_line_item.enrollment_key = enrollment_key
    invoice_line_item.invoice_key = invoice_key
    invoice_line_item.amount = 99.99
    invoice_line_item.put()
    return invoice_line_item

def create_invoice(provider_key, parent_key):
    """Creates a new Invoice"""
    invoice = Invoice()
    invoice.provider_key = provider_key
    invoice.parent_key = parent_key
    invoice.amount = 199.99
    invoice.put()
    return invoice