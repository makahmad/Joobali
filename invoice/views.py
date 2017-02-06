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
from invoice.invoice_util import get_invoice_enrollments
from parent.models import Parent
from child.models import Child

import json
import logging


logger = logging.getLogger(__name__)


def listInvoices(request):
	"""Handles invoice listing request. Returns invoices associated with the logged in user (provider or parent)"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')
	invoices = None
	provider = Provider.get_by_id(email)
	if not provider:
		invoices = Invoice.query(Invoice.parent_email == email)
	else:
		invoices = Invoice.query(Invoice.provider_key == provider.key)

    # TODO: handle parent invoice listing.

	results = []
	for invoice in invoices:
		results.append({
			'invoice_id': invoice.key.id(),
            'provider': invoice.provider_key.get().schoolName,
            'provider_customer_id': invoice.provider_key.get().customerId,
            'child': invoice.child_key.get().first_name,
            'amount' : invoice.amount,
            'due_date' : invoice.due_date.strftime('%m/%d/%Y'),
            'paid' : invoice.paid
        })
	return HttpResponse(json.dumps(results))


def setupAutopay(request):
	data = json.loads(request.body)
	invoice_id = data['invoice_id']
	source = data['source']
	invoice = None
	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)
		enrollments = get_invoice_enrollments(invoice)
		for enrollment in enrollments:
			enrollment.autopay_source_id = source
			enrollment.put()

	return HttpResponse("success")