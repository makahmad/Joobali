from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from django.http import HttpResponse

from login import models

import dwollav2

def home(request):
	client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
	account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')

	customers = account_token.get('customers')
	print customers.body['_embedded']['customers']
	return HttpResponse(customers.body['_embedded']['customers'])

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
})

def form(request):
	form = ProviderForm()
	if request.method == 'POST':
		provider = models.Provider()
		form = ProviderForm(request.POST)
		print 'FORM:::::::'
		print form.email.errors
		print form.email.filters
		form.validate()
		print 
		if form.validate():
			form.populate_obj(provider)
			query = models.Provider.query().filter(models.Provider.email == provider.email)
			result = query.fetch(1)
			if result:
				form.email.errors.append('error: user exists')
			else:
				provider.put()
				print "INFO: successfully stored Provider:" + str(provider)

				client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
				account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')
				request_body = {
				  'firstName': provider.firstName,
				  'lastName': provider.lastName,
				  'email': provider.email,
				  'ipAddress': '99.99.99.99'
				}
				customer = account_token.post('customers', request_body)
				return HttpResponseRedirect('/login')

	return render_to_response(
		'login/userform.html',
		{'form': form},
		template.RequestContext(request)
	)
