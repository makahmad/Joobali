from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from django.http import HttpResponse
from django import template

from login import models

import dwollav2

register = template.Library()

@register.filter(name='dateformat')
def dateformat(value):
    return value.strftime('%Y-%m-%d')


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

	form = ProviderForm()
	if request.method == 'GET':
		query = models.Provider.query().filter(models.Provider.email == "rongjian.lan@gmail.com")
		result = query.fetch(1)[0]

		if result:
			form = ProviderForm(obj=result)
		else:
			raise Exception('No Result Found.')

	print 'test:::::::'
	print form.dateOfBirth.data
	if request.method == 'POST':
		form = ProviderForm(request.POST)
		
		query = models.Provider.query().filter(models.Provider.email == request.POST.get('email'))

		provider = models.Provider()
		if query.fetch(1):
			provider = query.fetch(1)[0]

		print 'FORM:::::::'
		print form.email.errors
		print form.email.filters
		print provider.ssn
		form.validate()
		form.populate_obj(provider)
		print provider.ssn

		provider.put()
		print "INFO: successfully stored Provider:" + str(provider)

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
		  "dateOfBirth": provider.dateOfBirth.strftime('%Y-%m-%d'),
		  "ssn": provider.ssn
		}
		# TODO: store customer key in DB and use the real customer key in the url.
		customer_url = 'https://api-uat.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'
		customer = account_token.post(customer_url, request_body)
		

	return render_to_response(
		'users/index.html',
		{'form': form},
		template.RequestContext(request)
	)