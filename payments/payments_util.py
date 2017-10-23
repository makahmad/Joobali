import logging

from models import Payment
from invoice import invoice_util


logger = logging.getLogger(__name__)


def add_payment_maybe_for_invoice(provider, child, amount, payer, payment_date, payment_type, note, invoice=None, status=None, fee=0, dwolla_transfer_id=None):

    newPayment = Payment(provider_key=provider.key,child_key=child.key)

    if invoice:
        newPayment.invoice_key = invoice.key

    newPayment.amount = amount
    newPayment.balance = amount if status is None else 0 # If status is present that's a online transfer payment, we don't keep balance for online payment.
    newPayment.payer = payer
    newPayment.provider_email = provider.email
    newPayment.type = payment_type
    newPayment.note = note
    newPayment.date = payment_date
    newPayment.dwolla_transfer_id = dwolla_transfer_id
    newPayment.status = status
    newPayment.fee = fee
    newPayment.put()

    if newPayment.invoice_key and not status: # If status is present that's a online transfer payment, we don't actual pay the invoice until the transfer is completed (which is handled by webhooks)
        invoice_util.pay(invoice, newPayment)

    return newPayment