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
    # program_id = long(data['program_id'])
    payer = data['payer']
    payment_type = data['payment_type']
    amount = data['amount']
    payment_date = datetime.strptime(data['payment_date'], DATE_FORMAT).date()
    created_date = datetime.strptime(data['created_date'], DATE_FORMAT).date()

    provider = Provider.get_by_id(request.session.get('user_id'))
    child = Child.get_by_id(child_id)
    newPayment = Payment(provider_key=provider.key,child_key=child.key)
    newPayment.amount = amount
    newPayment.payer = payer
    newPayment.type = payment_type
    newPayment.date = payment_date
    newPayment.put()

    return HttpResponse('success')


def listInvoices(request):
    """Handles invoice listing request. Returns invoices associated with the logged in user (provider or parent)"""
    email = request.session.get('email')
    if not check_session(request):
        return HttpResponseRedirect('/login')
    invoices = None
    provider = Provider.query().filter(Provider.email == email).fetch(1)
    if not provider:
        invoices = Invoice.query(Invoice.parent_email == email)
    else:
        invoices = Invoice.query(Invoice.provider_email == email)

    results = []
    for invoice in invoices:
        results.append({
            'invoice_id': invoice.key.id(),
            'provider': invoice.provider_key.get().schoolName,
            'provider_customer_id': invoice.provider_key.get().customerId,
            'child': '%s %s' % (invoice.child_key.get().first_name, invoice.child_key.get().last_name),
            'amount': invoice.amount,
            'due_date': invoice.due_date.strftime('%m/%d/%Y'),
            'paid': invoice.is_paid(),
        })
    return HttpResponse(json.dumps(results))
