from common.session import check_session
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from django.http import HttpResponse
from django import template

from login import models

import dwollav2
import logging

logger = logging.getLogger(__name__)



def home(request):
	return HttpResponse('place holder')

stripFilter = lambda x: x.strip()  if x else ''
ProviderForm = model_form(models.Provider, field_args={
	'firstName': {
		'filters': [stripFilter],
	},
	'lastName': {
		'filters': [stripFilter],
	},
	'schoolName': {
		'filters': [stripFilter],
	},
	'email': {
		'filters': [stripFilter],
	},
	'password': {
		'filters': [stripFilter],
	},
	'phone': {
		'filters': [stripFilter],
	},
	'license': {
		'filters': [stripFilter],
	},
	'address': {
		'filters': [stripFilter],
	},
	'city': {
		'filters': [stripFilter],
	},
	'state': {
		'filters': [stripFilter],
	},
	'postalCode': {
		'filters': [stripFilter],
	},
	'ssn': {
		'filters': [stripFilter],
	}
})



def form(request):
	"""A form function to handle user profile form GET and POST requests"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')
	form = ProviderForm()
	if request.method == 'GET':
		query = models.Provider.query().filter(models.Provider.email == email)
		result = query.fetch(1)[0]

		if result:
			form = ProviderForm(obj=result)
		else:
			raise Exception('No Result Found.')

	if request.method == 'POST':
		form = ProviderForm(request.POST)
		
		query = models.Provider.query().filter(models.Provider.email == request.POST.get('email'))

		provider = models.Provider()
		if query.fetch(1):
			provider = query.fetch(1)[0]

		# memorize fields that's not in the form
		# TODO: think of a way to keep the fields that's not specified in the form,
		# right now the fields not specified will be set to None.
		customerId = provider.customerId
		password = provider.password

		form.validate()
		form.populate_obj(provider)
		# Restore the memorized fields
		provider.customerId = customerId
		provider.password = password

		provider.put()
		logger.info("INFO: successfully stored Provider:" + str(provider))

		client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
		account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')
		request_body = {
		  "firstName": provider.firstName,
		  "lastName": provider.lastName,
		  "email": provider.email,
		  #"ipAddress": "10.10.10.10", # TODO: use real IP
		  "type": "personal",
		  "phone": provider.phone,
		  "address1": provider.address,
		  "city": provider.city,
		  "state": provider.state,
		  "postalCode": provider.postalCode,
		  "dateOfBirth": provider.dateOfBirth.strftime('%m/%d/%Y') if provider.dateOfBirth else '',
		  "ssn": provider.ssn
		}
		# TODO: store customer key in DB and use the real customer key in the url.
		customer_url = getCustomerUrl(email)
		customer = account_token.post(customer_url, request_body)


	return render_to_response(
		'users/index.html',
		{'form': form},
		template.RequestContext(request)
	)

def getCustomerUrl(email):
	"""Gets the dwolla customer identifying URL"""
	result = models.Provider.get_by_id(email)
	if result is not None:
		return result.customerId
	raise Exception('user does not exist')