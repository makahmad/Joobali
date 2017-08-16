import logging

from models import Payment
from invoice import invoice_util


logger = logging.getLogger(__name__)


def add_payment_maybe_for_invoice(provider, child, amount, payer, payment_date, payment_type, note, invoice=None):

    newPayment = Payment(provider_key=provider.key,child_key=child.key)

    if invoice:
        newPayment.invoice_key = invoice.key

    newPayment.amount = amount
    newPayment.balance = amount
    newPayment.payer = payer
    newPayment.provider_email = provider.email
    newPayment.type = payment_type
    newPayment.note = note
    newPayment.date = payment_date
    newPayment.put()

    if newPayment.invoice_key:
        invoice_util.pay(invoice, newPayment)

    return newPayment