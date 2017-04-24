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
from child import child_util
from enrollment import enrollment_util
from django.template import loader
from invoice import invoice_util
from common.pdf import render_to_pdf
from google.appengine.ext import ndb
from os import environ

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

	description = data['description']
	amount = data['amount']
	due_date = datetime.strptime(data['due_date'], DATE_FORMAT).date()
	created_date = datetime.strptime(data['created_date'], DATE_FORMAT).date()
	if 'all_children' in data:
		print data['all_children']
		for child_id in data['all_children']:
			provider = Provider.get_by_id(request.session.get('user_id'))
			child = Child.get_by_id(child_id)
			invoice = invoice_util.create_invoice(provider, child, created_date, due_date, None, amount)
			invoice_util.create_invoice_line_item(None, invoice, None, None, None,
				description, amount)
	else:
		child_id = long(data['child_id'])
		program_id = long(data['program_id'])

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
			'id': invoice.key.id(),
			'invoice_id': invoice.key.id(),
            'provider': invoice.provider_key.get().schoolName,
            'provider_customer_id': invoice.provider_key.get().customerId,
			'child_id': invoice.child_key.id(),
            'child': '%s %s' % (invoice.child_key.get().first_name, invoice.child_key.get().last_name),
			'original_amount': invoice_util.sum_up_original_amount_due(invoice),
            'amount' : invoice.amount,
            'due_date' : invoice.due_date.strftime('%m/%d/%Y'),
            'paid' : invoice.is_paid(),
        })
	return HttpResponse(json.dumps(results))

def viewInvoice(request):
	""" Display a specific invoice content"""
	if not check_session(request):
		return HttpResponseRedirect('/login')

	invoice_id = request.GET['id']

	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)

		(start_date, end_date) = invoice_util.get_invoice_period(invoice)
		provider = invoice.provider_key.get()
		parent = Parent.query(Parent.email == invoice.parent_email).fetch(1)[0]
		child = invoice.child_key.get()

		lineItems = InvoiceLineItem.query(ancestor=invoice.key)
		total = 0
		items = []
		for lineItem in lineItems:
			description = ''
			if lineItem.program_name:
				description = lineItem.program_name
			if lineItem.description:
				if description != '':
					description = '%s (%s)' % (description, lineItem.description)
				else:
					description = lineItem.description
			items.append({
				'description': description,
				'amount': lineItem.amount,
			})
			total += lineItem.amount
		if total != invoice.amount:
			HttpResponse("Something is wrong when retrieving the invoice.")

		http_prefix = 'http://' if environ.get('IS_DEV') else 'https://'
		root_path = http_prefix + request.get_host()

		note = provider.lateFeeInvoiceNote if invoice.is_late() else provider.generalInvoiceNote
		data = {
			'invoice_id': invoice.key.id(),
			'invoice_date': invoice.date_created.strftime('%m/%d/%Y'),
            # 'provider_street': provider.address,
			# 'provider_city_state_postcode': '%s, %s, %s' % (provider.city, provider.state, provider.postalCode),
			'provider_name': provider.schoolName,
            'provider_phone_number': provider.phone,
            'child_name': '%s %s' % (child.first_name, child.last_name),
            'parent_name' : '%s %s' % (parent.first_name, parent.last_name),
			'start_date': start_date.strftime('%m/%d/%Y') if start_date else 'N/A',
			'end_date': end_date.strftime('%m/%d/%Y') if end_date else 'N/A',
			'due_date': invoice.due_date.strftime('%m/%d/%Y'),
			'parent_id': parent.key.id(),
			'total': invoice.amount,
			'items': items,
			'logo_url': root_path + '/profile/getproviderlogo?id=' + str(provider.key.id()),
			'note': note,
        }
		print data
		return render_to_pdf(
			'invoice/invoice_content.html',
			data
		)

def setupAutopay(request):
	data = json.loads(request.body)
	invoice_id = data['invoice_id']
	source = data['source']
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
	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)
		invoice.status = Invoice._POSSIBLE_STATUS['MARKED_PAID']
		invoice.put()
	return HttpResponse("success")

def adjust_invoice(request):
	data = json.loads(request.body)
	invoice_id = data['invoice_id']
	amount = data['amount']
	reason = data['reason']
	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)
		invoice_util.adjust_invoice(invoice, amount, reason)
		invoice.put()
	return HttpResponse("success")

def list_invoice_by_child(request):
    status = "failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    provider_id = request.session.get('user_id')
    child_id = long(request.GET.get('child_id'))
    logger.info('provider_id %s, child_id %s' % (provider_id, child_id))
    child_key = Child.generate_key(child_id)
    provider_key = Provider.generate_key(provider_id)
    all_invoices = invoice_util.list_invoice_by_provider_and_child(provider_key=provider_key, child_key=child_key)
    invoices = []
    for invoice in all_invoices:
        if not invoice.is_paid():
            invoices.append(invoice)
    response = HttpResponse(json.dumps([JEncoder().encode(invoice) for invoice in invoices]))
    logger.info("response is %s" % response)
    return response