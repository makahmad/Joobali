from common.json_encoder import JEncoder
from common.session import check_session
from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from time import strftime, strptime
from datetime import datetime, date, time
from login.models import Provider, Unique
from parent.models import Parent
from parent import parent_util
from invoice.models import Invoice
from invoice.models import InvoiceLineItem
from invoice.invoice_util import get_invoice_enrollments
from manageprogram.models import Program
from child.models import Child
from child import child_util
from payments.models import Payment

from django.template import loader
from invoice import invoice_util
from common.pdf import render_to_pdf
from common import dwolla
from google.appengine.ext import ndb
from common import datetime_util

import json
import logging

DATE_FORMAT = '%m/%d/%Y'
logger = logging.getLogger(__name__)


def add_payment(request):
    """Handles invoice listing request. Returns invoices associated with the logged in user (provider or parent)"""
    email = request.session.get('email')
    if not check_session(request):
        return HttpResponseRedirect('/login')

    data = json.loads(request.body)
    child_id = long(data['child_id'])

    try:
        invoice_id = data['invoice_id']
    except KeyError:
        invoice_id = None

    payer = data['payer']

    payment_type = data['payment_type']

    try:
        note = data['note']
    except KeyError:
        note = None
    amount = data['amount']
    payment_date = datetime_util.local_to_utc(datetime.strptime(data['payment_date'], DATE_FORMAT))

    provider = Provider.get_by_id(request.session.get('user_id'))
    child = Child.get_by_id(child_id)

    newPayment = Payment(provider_key=provider.key,child_key=child.key)

    if invoice_id:
        newPayment.invoice_key = ndb.Key('Invoice', invoice_id)

    newPayment.amount = amount
    newPayment.balance = amount
    newPayment.payer = payer
    newPayment.provider_email = provider.email
    newPayment.type = payment_type
    newPayment.note = note
    newPayment.date = payment_date
    newPayment.put()

    if newPayment.invoice_key:
        invoice_util.pay(newPayment.invoice_key.get(), newPayment)
    return HttpResponse('success')


def listPayments(request):
    """Handles payment listing request. Returns payments associated with the logged in user (provider or parent)"""
    email = request.session.get('email')
    if not check_session(request):
        return HttpResponseRedirect('/login')
    payments = None
    provider = Provider.query().filter(Provider.email == email).fetch(1)
    if not provider:
        parent = Parent.query().filter(Parent.email == email).fetch(1)
        payments = []
        if parent:
            for child in child_util.list_child_by_parent(parent[0].key):
                payments.extend(Payment.query(Payment.child_key == child.key))
    else:
        payments = Payment.query(Payment.provider_email == email)

    results = []
    for payment in payments:
        results.append({
            'child': '%s %s' % (payment.child_key.get().first_name, payment.child_key.get().last_name),
            'amount': float(payment.amount),
            'balance': float(payment.balance),
            'date': datetime_util.utc_to_local(payment.date).strftime('%m/%d/%Y'),
            'type': payment.type,
            'payer': payment.payer,
            'provider_amount': float(payment.amount),
            'fee': 0,
            'invoice': payment.invoice_key.id() if payment.invoice_key else 'NA',
            'note': payment.note,
        })
    results.extend(list_dwolla_payments(email))
    return HttpResponse(json.dumps(results))


def list_dwolla_payments(email):
    """Returns dwolla payments associated with the logged in user (provider or parent)"""
    invoices = []

    unique_customer = Unique.get_by_id(email)
    logger.info("Retrieving Dwolla Payments...")
    if unique_customer:
        if unique_customer.provider_key:
            for invoice in Invoice.query(Invoice.provider_key == unique_customer.provider_key).fetch():
                invoices.append(invoice)
        elif unique_customer.parent_key:
            for invoice in Invoice.query(Invoice.parent_email == email).fetch():
                invoices.append(invoice)


    logger.info("Retrieving Dwolla Payments... Invoices: %s" % invoices)
    results = []
    for invoice in invoices:
        if invoice.dwolla_transfer_id:
            transfer = dwolla.get_dwolla_transfer(invoice.dwolla_transfer_id)
            amount = transfer['amount']
            source_customer_url = transfer['source_customer_url']
            status = transfer['status']
            date = transfer['created_date']
            parent = parent_util.get_parent_by_dwolla_id(source_customer_url)

            fee_amount = 0
            if transfer['fee_transfer_url']:
                fee_transfer = dwolla.get_fee_transfer(transfer['fee_transfer_url'])
                fee_amount = fee_transfer['amount']

            if parent:
                results.append({
                    'child': '%s %s' % (invoice.child_first_name, invoice.child_last_name),
                    'amount': float(amount),
                    'balance': float(0),
                    'provider_amount': float(amount) - float(fee_amount),
                    'fee': fee_amount,
                    'date': date,
                    'type': 'Online Transfer',
                    'payer': '%s %s' % (parent.first_name, parent.last_name),
                    'invoice': invoice.key.id() if invoice else 'NA',
                    'note': '',
                })

    return results