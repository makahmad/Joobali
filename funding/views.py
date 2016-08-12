from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from funding import models
#from django.core.exceptions import ValidationError

from dwollav2.error import ValidationError
import sys 
import json
import dwollav2


stripFilter = lambda x: x.strip()  if x else ''
FundingForm = model_form(models.Funding, field_args={
	'name': {
		'filters': [stripFilter],
	},
	'type': {
		'filters': [stripFilter],
	},
	'accountNumber': {
		'filters': [stripFilter],
	},
	'routingNumber': {
		'filters': [stripFilter],
	}
})

test_customer_url = 'https://api-uat.dwolla.com/customers/bb72af0b-8a9f-4b40-ab94-c20cd0900e9c'

def index(request):
	form = FundingForm()
	if request.method == 'POST':
		form = FundingForm(request.POST)

		name = request.POST.get('name');
		type = request.POST.get('type');
		accountNumber = request.POST.get('accountNumber');
		routingNumber = request.POST.get('routingNumber');
		print name
		print type
		print accountNumber
		print routingNumber

		form.validate()
		client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
		account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')
		request_body = {
		  "routingNumber": routingNumber,
		  "accountNumber": accountNumber,
		  "type": type,
		  "name": name
		}
		try:
			funding = account_token.post('%s/funding-sources' % test_customer_url, request_body)
		except ValidationError as err: # ValidationError as err
			print "EEEEEEEERRRRRRRRRRRRRRR";
			# e.g.: {"code":"ValidationError","message":"Validation error(s) present. See embedded errors list for more details.","_embedded":{"errors":[{"code":"Invalid","message":"Invalid parameter.","path":"/routingNumber"}]}}
			if 'routing' in err.body['_embedded']['errors'][0]['path']:
				form.routingNumber.errors.append('Invalid Routing Number')
			return render_to_response(
				'funding/index.html',
				{'form': form},
				template.RequestContext(request)
			)
		return HttpResponseRedirect('/funding')
	return render_to_response(
		'funding/index.html',
		{},
		template.RequestContext(request)
	)

def listFunding(request):
	client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
	account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')
	request_body = {
	  "routingNumber": 'test',
	  "accountNumber": 'test',
	  "type": 'test',
	  "name": 'test'
	}

	fundings = [];
	funding_sources = account_token.get('%s/funding-sources' % test_customer_url)
	for funding in funding_sources.body['_embedded']['funding-sources']:
		fundings.append({
			  "status": funding['status'],
			  "type": funding['type'],
			  "name": funding['name']
			})
		#funding_source = account_token.get(funding['_links']['self']['href']);
		#print funding['_links']['self']['href'];
		#print funding_source.body
		#print funding_source.body['_embedded'];
	return HttpResponse(json.dumps([JEncoder().encode(funding) for funding in fundings]))

class JEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return o.isoformat()	  # Or whatever other date format you're OK with...