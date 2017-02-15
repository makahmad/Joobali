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
from parent.models import Parent
from child.models import Child
from django.template import loader
from invoice import invoice_util
from common.pdf import render_to_pdf

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

def viewInvoice(request):
	""" Display a specific invoice content"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')
	invoices = None
	print email
	provider = Provider.query().filter(Provider.email == email).get()
	if not provider:
		invoices = Invoice.query(Invoice.parent_email == email)
	else:
		invoices = Invoice.query(Invoice.provider_key == provider.key)

	# TODO: handle parent invoice listing.

	for invoice in invoices:
		(start_date, end_date) = invoice_util.get_invoice_period(invoice)
		parent = Parent.query(Parent.email == invoice.parent_email).fetch(1)[0]
		items = []
		lineItems = InvoiceLineItem.query(ancestor=invoice.key)
		for lineItem in lineItems:
			items.append({
				'program_name': lineItem.program_name,
				'amount': lineItem.amount,
			})
		data = {
			'invoice_id': invoice.key.id(),
            'provider_street': provider.address,
            'provider_phone_number': provider.phone,
            'child_name': invoice.child_key.get().first_name + ', ' + invoice.child_key.get().last_name,
            'parent_name' : parent.first_name + ', ' + parent.last_name,
			'start_date': start_date.strftime('%m/%d/%Y'),
			'end_date': end_date.strftime('%m/%d/%Y'),
			'due_date': invoice.due_date.strftime('%m/%d/%Y'),
			'parent_id': parent.key.id(),
			'total': invoice.amount,
			'items': items,
        }
		return render_to_pdf(
			'invoice/invoice_content.html',
			data
		)

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