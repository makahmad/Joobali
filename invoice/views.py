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
from common.dwolla import get_funding_source, get_dwolla_transfer, cancel_transfer
from common.email.autopay import send_autopay_cancelled_email, send_autopay_scheduled_email
from common import datetime_util
from common.request import get_host_from_request
import json
import logging


DATE_FORMAT = '%m/%d/%Y'
logger = logging.getLogger(__name__)
support_phone = '301-538-6558'

def add_invoice(request):
	"""Handles invoice listing request. Returns invoices associated with the logged in user (provider or parent)"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')

	data = json.loads(request.body)

	description = data['description']
	send_email = data['send_email']
	amount = data['amount']
	due_date = datetime_util.local_to_utc(datetime.strptime(data['due_date'], DATE_FORMAT))
	if 'all_children' in data:
		if 'program_id' in data:
			for child in child_util.list_child_by_provider_program(request.session.get('user_id'), long(data['program_id'])):
				provider = Provider.get_by_id(request.session.get('user_id'))
				invoice = invoice_util.create_invoice(provider, child, due_date, None, amount, True, send_email)
				invoice_util.create_invoice_line_item(None, invoice, None, None, None,
													  description, amount)
		else:
			for child_id in data['all_children']:
				provider = Provider.get_by_id(request.session.get('user_id'))
				child = Child.get_by_id(child_id)
				invoice = invoice_util.create_invoice(provider, child, due_date, None, amount, False, send_email)
				invoice_util.create_invoice_line_item(None, invoice, None, None, None,
					description, amount)
	else:
		child_id = long(data['child_id'])
		if 'program_id' in data:
			program_id = long(data['program_id'])

			provider = Provider.get_by_id(request.session.get('user_id'))
			child = Child.get_by_id(child_id)
			program = ndb.Key('Provider', provider.key.id(), 'Program', program_id).get()
			enrollment = enrollment_util.list_enrollment_by_provider_and_child_and_program(
				provider_key=provider.key, child_key=ndb.Key('Child', child_id), program_key=program.key)[0]
			invoice = invoice_util.create_invoice(provider, child, due_date, enrollment.autopay_source_id,
												  amount, True, send_email)
			invoice_util.create_invoice_line_item(
				ndb.Key("Provider", provider.key.id(), "Enrollment", enrollment.key.id()), invoice, program, None, None,
				description, amount)
		else:
			provider = Provider.get_by_id(request.session.get('user_id'))
			child = Child.get_by_id(child_id)
			invoice = invoice_util.create_invoice(provider, child, due_date, None,
												  amount, False, send_email)
			invoice_util.create_invoice_line_item(None, invoice, None, None, None,
				description, amount)


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
		data = {
			'id': invoice.key.id(),
			'invoice_id': invoice.key.id(),
            'provider': invoice.provider_key.get().schoolName,
            'provider_customer_id': invoice.provider_key.get().customerId,
			'child_id': invoice.child_key.id(),
            'child': '%s %s' % (invoice.child_key.get().first_name, invoice.child_key.get().last_name),
			'original_amount': invoice_util.sum_up_original_amount_due(invoice),
            'amount' : invoice.amount,
            'is_recurring' : invoice.is_recurring,
            'due_date' : datetime_util.utc_to_local(invoice.due_date).strftime('%m/%d/%Y'),
            'paid' : invoice.is_paid(),
			'processing': invoice.is_processing(),
            'status' : "Payment Processing" if invoice.is_processing() else ("Paid" if invoice.is_paid() else 'Unpaid'),
			'autopay_source_id': invoice.autopay_source_id if invoice.autopay_source_id else None,
			'snippet': invoice_util.get_invoice_snippet(invoice)
        }
		if invoice.is_processing() and invoice.dwolla_transfer_id:
			dwolla_transfer = get_dwolla_transfer(invoice.dwolla_transfer_id)
			if 'cancel' in dwolla_transfer:
				data['cancel'] = dwolla_transfer['cancel']
		results.append(data)
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

		lineItems = InvoiceLineItem.query(ancestor=invoice.key).filter(InvoiceLineItem.payment_key == None)
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

		http_prefix = 'http://' if environ.get('IS_DEV') == 'True' else 'https://'
		root_path = http_prefix + request.get_host()

		note = invoice.late_fee_note if invoice.is_over_due() else invoice.general_note
		data = {
			'invoice_id': invoice.key.id(),
			'invoice_date': datetime_util.utc_to_local(invoice.time_created).strftime('%m/%d/%Y') if invoice.time_created else '',
            'provider_street': provider.addressLine1 + (", %s" % provider.addressLine2) if provider.addressLine2 else provider.addressLine1,
			'provider_city_state_postcode': '%s, %s, %s' % (provider.city, provider.state, provider.zipcode),
			'provider_name': provider.schoolName,
            'provider_phone_number': provider.phone,
            'child_name': '%s %s' % (child.first_name, child.last_name),
            'parent_name' : '%s %s' % (parent.first_name, parent.last_name),
			'start_date': datetime_util.utc_to_local(start_date).strftime('%m/%d/%Y') if start_date else 'N/A',
			'end_date': datetime_util.utc_to_local(end_date).strftime('%m/%d/%Y') if end_date else 'N/A',
			'due_date': datetime_util.utc_to_local(invoice.due_date).strftime('%m/%d/%Y'),
			'parent_id': parent.key.id(),
			'total': total,
			'items': items,
			'logo_url': root_path + '/profile/getproviderlogo?id=' + str(provider.key.id()) if provider.logo else None,
			'note': note,
			'tin': provider.tin,
			'autopay_source_id': invoice.autopay_source_id if invoice.autopay_source_id else None,
        }
		print data
		return render_to_pdf(
			'invoice/invoice_content.html',
			data
		)

def setupAutopay(request):
	data = json.loads(request.body)
	parent = Parent.get_by_id(request.session.get('user_id'))
	invoice_id = data['invoice_id']
	source = data['source']
	today = date.today()
	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)
		enrollments = get_invoice_enrollments(invoice)
		for enrollment in enrollments:
			enrollment.autopay_source_id = source
			enrollment.pay_days_before = 5 # TODO(rongjian): allow users to set it
			enrollment.put()

			## Send Confirm Email
			program = enrollment.program_key.get()
			amount = program.fee
			schedule = None
			if program.billingFrequency == 'Weekly':
				schedule = program.weeklyBillDay + ' every week'
			else:
				if program.monthlyBillDay == 'Last Day':
					schedule = ' the last day of every month'
				else:
					schedule = ' the ' + program.monthlyBillDay + 'th of every month'

			provider = enrollment.key.parent().get()

			source_funding_source = get_funding_source(source)

			first_transfer_date = enrollment.start_date
			if first_transfer_date is None:
				first_transfer_date = program.startDate
			while first_transfer_date.date() < today:
				first_transfer_date = invoice_util.get_next_due_date(first_transfer_date, program.billingFrequency)
			child = enrollment.child_key.get()
			data = {
				'child_name': child.first_name if child.first_name else '',
				'program_name': program.programName if program.programName else '',
				'first_name': provider.firstName if provider.firstName else '',
				'transfer_type': 'Online',
				'amount': '$' + str(amount),
				'account_name': source_funding_source['name'],
				'recipient': provider.schoolName,
				'schedule': schedule,
				'next_payment_date': first_transfer_date.strftime('%A, %B %d %Y'),
				'host': get_host_from_request(request.get_host()),
				'support_phone': support_phone,
			}
			send_autopay_scheduled_email('%s %s' % (parent.first_name if parent.first_name else '', parent.last_name if parent.last_name else ''), parent.email, data)
			## End Send Confirm Email

			for invoice in invoice_util.get_enrollment_invoices(enrollment):
				if not invoice.is_paid():
					invoice.autopay_source_id = source
					invoice.put()

	return HttpResponse("success")

def cancelAutopay(request):
	parent = Parent.get_by_id(request.session.get('user_id'))
	data = json.loads(request.body)
	invoice_id = data['invoice_id']
	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)
		enrollments = get_invoice_enrollments(invoice)
		for enrollment in enrollments:
			source = enrollment.autopay_source_id

			## Send Confirm Email
			program = enrollment.program_key.get()
			amount = program.fee
			schedule = None
			if program.billingFrequency == 'Weekly':
				schedule = program.weeklyBillDay + ' every week'
			else:
				if program.monthlyBillDay == 'Last Day':
					schedule = ' the last day of every month'
				else:
					schedule = ' the ' + program.monthlyBillDay + 'th of every month'

			provider = enrollment.key.parent().get()

			source_funding_source = get_funding_source(source)
			child = enrollment.child_key.get()
			data = {
				'date_cancelled': date.today().strftime(DATE_FORMAT),
				'child_name': child.first_name if child.first_name else '',
				'program_name': program.programName if program.programName else '',
				'first_name': provider.firstName if provider.firstName else '',
				'transfer_type': 'Online',
				'amount': '$' + str(amount),
				'account_name': source_funding_source['name'],
				'recipient': provider.schoolName,
				'schedule': schedule,
				'host': get_host_from_request(request.get_host()),
				'support_phone': support_phone,
			}
			send_autopay_cancelled_email('%s %s' % (parent.first_name if parent.first_name else '', parent.last_name if parent.last_name else ''), parent.email, data)
			## End Send Confirm Email

			for invoice in invoice_util.get_enrollment_invoices(enrollment):
				if not invoice.is_paid():
					invoice.autopay_source_id = None
					invoice.put()

			enrollment.autopay_source_id = None
			enrollment.pay_days_before = None
			enrollment.put()

	return HttpResponse("success")

def cancelPayment(request):
	parent = Parent.get_by_id(request.session.get('user_id'))
	data = json.loads(request.body)
	invoice_id = data['invoice_id']
	if invoice_id:
		invoice = Invoice.get_by_id(invoice_id)
		if invoice.dwolla_transfer_id:
			dwolla_transfer = get_dwolla_transfer(invoice.dwolla_transfer_id)
			if 'cancel' in dwolla_transfer:
				cancel_transfer(dwolla_transfer['cancel'])
				invoice.status = invoice._POSSIBLE_STATUS['CANCELLED']
				invoice.put()
			else:
				return HttpResponse("Failure: the payment is being processed and can't be cancelled at this moment.")
		else:
			return HttpResponse("Failure: no payment is associated with this invoice.")

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
		snippet = invoice_util.get_invoice_snippet(invoice)
		if not invoice.is_paid() or not invoice.is_processing():
			invoice_dict = invoice.to_dict()
			invoice_dict['id'] = invoice.key.id()
			invoice_dict['snippet'] = snippet
			invoices.append(invoice_dict)
    response = HttpResponse(json.dumps([JEncoder().encode(invoice) for invoice in invoices]))
    logger.info("response is %s" % response)
    return response