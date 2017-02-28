from common.json_encoder import JEncoder
from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from invoice.models import Invoice
from funding import models
from login.models import Provider
from funding import funding_util
#from django.core.exceptions import ValidationError
from common.session import check_session
from dwollav2.error import ValidationError
from common.dwolla import create_account_token
import json
import dwollav2
import logging

logger = logging.getLogger(__name__)
account_token = create_account_token('sandbox')

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
# test_customer_url = 'https://api-uat.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'


def index(request):
    if not request.session.get('email'):
        return HttpResponseRedirect('/login')
    customer_url = request.session.get('dwolla_customer_url')
    form = FundingForm()
    if request.method == 'POST':
        form = FundingForm(request.POST)

        name = request.POST.get('name');
        type = request.POST.get('type');
        accountNumber = request.POST.get('accountNumber');
        routingNumber = request.POST.get('routingNumber');

        form.validate()
        request_body = {
          "routingNumber": routingNumber,
          "accountNumber": accountNumber,
          "type": type,
          "name": name
        }
        try:
            funding = account_token.post('%s/funding-sources' % customer_url, request_body)
        except ValidationError as err: # ValidationError as err
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
    if not request.session.get('email'):
        return HttpResponseRedirect('/login')
    customer_url = request.session.get('dwolla_customer_url')

    fundings = funding_util.list_fundings(customer_url)
        # Sample code to get funding source info
        #funding_source = account_token.get(funding['_links']['self']['href']);
        #print funding['_links']['self']['href'];
        #print funding_source.body
        #print funding_source.body['_embedded'];
    return HttpResponse(json.dumps([JEncoder().encode(funding) for funding in fundings]))

def listProvider(request):

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
    if not request.session.get('email'):
        return HttpResponseRedirect('/login')
    customer_url = request.session.get('dwolla_customer_url')
    logger.info("account_token.post(%s)" % (customer_url + '/iav-token'))
    customer = account_token.post(customer_url + '/iav-token')

    return HttpResponse(customer.body['token'])

def makeTransfer(request):

    data = json.loads(request.body)
    invoice_id = data['invoice_id']
    invoice = None
    if invoice_id:
        invoice = Invoice.get_by_id(invoice_id)
        if invoice.amount != data['amount']:
            return HttpResponse("failure: payment amount must be equal to invoice amount")
    try:
        funding_util.make_transfer(data['destination'], data['source'], data['amount'])
    except ValidationError as err:
        return HttpResponse(err.body['_embedded']['errors'][0]['message'])
    # print transfer.headers['location'] # => 'https://api.dwolla.com/transfers/74c9129b-d14a-e511-80da-0aa34a9b2388'

    invoice.paid = True
    invoice.put()
    return HttpResponse("success")

def funding(request):
    
    funding_source_url = 'https://api.dwolla.com/funding-sources/692486f8-29f6-4516-a6a5-c69fd2ce854c'

    funding_source = account_token.get(funding_source_url)
    return HttpResponse(funding_source.body['_embedded'])

def getGeneralBilling(request):
    """Handles get general billing details (i.e. Provider model)"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])
    if provider is not None:
        return HttpResponse(json.dumps([JEncoder().encode(provider)]))

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))

def updateGeneralBilling(request):
    """Updates the general billing details"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if not request.session['is_provider']:
        return HttpResponseRedirect('/login')

    generalBilling = json.loads(request.body)

    # provider general billing update
    provider = Provider.get_by_id(request.session['user_id'])
    provider.lateFee = float(generalBilling['lateFee'])
    provider.graceDays = int(generalBilling['graceDays'])
    provider.put()

    return HttpResponse('success')