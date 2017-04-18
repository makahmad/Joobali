from common.json_encoder import JEncoder
from common.session import check_session
from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from time import strftime, strptime
from datetime import datetime, date, time
from login.models import Provider
from invoice.models import Invoice
from invoice.models import InvoiceLineItem
from invoice.invoice_util import get_invoice_enrollments
from manageprogram.models import Program
from child.models import Child
from payments.models import Payment

from django.template import loader
from invoice import invoice_util
from common.pdf import render_to_pdf
from google.appengine.ext import ndb

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
    payment_date = datetime.strptime(data['payment_date'], DATE_FORMAT).date()
    created_date = datetime.strptime(data['created_date'], DATE_FORMAT).date()

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
    newPayment.date_created = created_date
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
        payments = []
    else:
        payments = Payment.query(Payment.provider_email == email)

    results = []
    for payment in payments:
        results.append({
            'child': '%s %s' % (payment.child_key.get().first_name, payment.child_key.get().last_name),
            'amount': payment.amount,
            'date': payment.date.strftime('%m/%d/%Y'),
            'type': payment.type,
            'payer': payment.payer,
            'invoice': payment.invoice_key.id() if payment.invoice_key else 'NA',
            'note': payment.note,
        })
    return HttpResponse(json.dumps(results))
