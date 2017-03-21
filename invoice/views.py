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
from enrollment import enrollment_util
from django.template import loader
from invoice import invoice_util
from common.pdf import render_to_pdf
from google.appengine.ext import ndb

import json
import logging


DATE_FORMAT = '%m/%d/%Y'
logger = logging.getLogger(__name__)

def add_invoice(request):
	"""Handles invoice listing request. Returns invoices associated with the logged in user (provider or parent)"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')

	data = json.loads(request.body)
	child_id = long(data['child_id'])
	program_id = long(data['program_id'])
	description = data['description']
	amount = data['amount']
	due_date = datetime.strptime(data['due_date'], DATE_FORMAT).date()
	created_date = datetime.strptime(data['created_date'], DATE_FORMAT).date()

	provider = Provider.get_by_id(request.session.get('user_id'))
	child = Child.get_by_id(child_id)
	program = ndb.Key('Provider', provider.key.id(), 'Program', program_id).get()
	enrollment = enrollment_util.list_enrollment_by_provider_and_child_and_program(
		provider_id=provider.key.id(), child_key=ndb.Key('Child', child_id), program_key=program.key)[0]
	invoice = invoice_util.create_invoice(provider, child, created_date, due_date, enrollment.autopay_source_id, amount)
	invoice_util.create_invoice_line_item(ndb.Key("Provider", provider.key.id(), "Enrollment", enrollment.key.id()), invoice, program, None, None, description, amount)

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
            'amount' : invoice.amount,
            'due_date' : invoice.due_date.strftime('%m/%d/%Y'),
            'paid' : invoice.is_paid(),
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
		total = 0
		for lineItem in lineItems:
			items.append({
				'program_name': lineItem.program_name,
				'amount': lineItem.amount,
			})
			total += lineItem.amount
		if total != invoice.amount:
			HttpResponse("error")
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
			enrollment.pay_days_before = 5 # TODO(rongjian): allow users to set it
			enrollment.put()

	return HttpResponse("success")

def markPaid(request):
	data = json.loads(request.body)
	invoice_id = data['invoice_id']
	invoice = None
	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)
		invoice.status = Invoice._POSSIBLE_STATUS['MARKED_PAID']
		invoice.put()
	return HttpResponse("success")