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

# Zilong's ID: eeb997f4-e6b2-40bf-9f35-863f8769202c
# Rongjian's ID (rongjian@joobali.com): 45ad438b-dc6f-4210-b9d7-f651a870265b
# Rongjian's ID (rongjian@google.net): 199f1583-de16-4d83-868c-ef272942e636
# Rongjian - verified ID (rongjian.lan@gmail.com): 255b92a7-300b-42fc-b72f-5301c0c6c42e
# Bei's ID: f4871302-e98d-4d87-808f-31c6424199e4
# Choose the one as test customer.
test_customer_url = 'https://api-uat.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'

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
	#request_body = {
	#  "routingNumber": 'test',
	#  "accountNumber": 'test',
	#  "type": 'test',
	#  "name": 'test'
	#}

	fundings = [];
	funding_sources = account_token.get('%s/funding-sources' % test_customer_url)
	for funding in funding_sources.body['_embedded']['funding-sources']:
		print funding
		fundings.append({
			  "status": funding['status'],
			  "type": funding['type'],
			  "name": funding['name'],
			  "id": funding['id']
			})
		#funding_source = account_token.get(funding['_links']['self']['href']);
		#print funding['_links']['self']['href'];
		#print funding_source.body
		#print funding_source.body['_embedded'];
	return HttpResponse(json.dumps([JEncoder().encode(funding) for funding in fundings]))

def listProvider(request):
	client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
	account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')

	customers = account_token.get('customers')
	providers = [];
	for customer in customers.body['_embedded']['customers']:
		providers.append({
			"firstName": customer['firstName'],
			"lastName": customer['lastName'],
			"id": customer['id']

		})
	return HttpResponse(json.dumps([JEncoder().encode(provider) for provider in providers]))

def getIAVToken(request):
	client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
	account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')

	customer = account_token.post(test_customer_url + '/iav-token')

	return HttpResponse(customer.body['token'])

def makeTransfer(request):
	client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
	account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')
	
	data = json.loads(request.body)
	print data
	request_body = {
	  '_links': {
	    'destination': {
	      'href': 'https://api.dwolla.com/customers/' + data['destination']
	    },
	    'source': {
	      'href': 'https://api.dwolla.com/funding-sources/' + data['source']
	    }
	  },
	  'amount': {
	    'currency': 'USD',
	    'value': data['amount']
	  }
	};
	transfer = account_token.post('transfers', request_body)
	print transfer.headers['location'] # => 'https://api.dwolla.com/transfers/74c9129b-d14a-e511-80da-0aa34a9b2388'

	return HttpResponse("success")

def funding(request):
	client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
	account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')
    
	funding_source_url = 'https://api.dwolla.com/funding-sources/692486f8-29f6-4516-a6a5-c69fd2ce854c'

	funding_source = account_token.get(funding_source_url)
	print funding_source
	return HttpResponse(funding_source.body['_embedded'])

class JEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return o.isoformat()	  # Or whatever other date format you're OK with...