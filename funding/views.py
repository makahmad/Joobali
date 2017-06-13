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
        if invoice.is_paid():
            return HttpResponse("failure: the invoice has already been paid")
        if invoice.dwolla_transfer_id and invoice.is_processing():
            return HttpResponse("failure: payment for this invoice is in process")

    try:
        funding_util.make_transfer(data['destination'], data['source'], data['amount'], invoice)
    except ValidationError as err:
        return HttpResponse(err.body['_embedded']['errors'][0]['message'])
    # print transfer.headers['location'] # => 'https://api.dwolla.com/transfers/74c9129b-d14a-e511-80da-0aa34a9b2388'

    return HttpResponse("success")

def removeFunding(request):
    data = json.loads(request.body)
    funding_source_id = data['funding_source_id']
    funding_source_url = 'https://api-uat.dwolla.com/funding-sources/%s' % funding_source_id

    try:
        account_token.post(funding_source_url, { 'removed': True })
    except ValidationError as err:
        return HttpResponse(err.body['_embedded']['errors'][0]['message'])
    return HttpResponse("success")

def getGeneralBilling(request):
    """Handles get general billing details (i.e. Provider model)"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])
    if provider is not None:
        provider.logo = None
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

    try:
        provider.lateFeeInvoiceNote = generalBilling['lateFeeInvoiceNote']
    except KeyError:
        None

    try:
        provider.generalInvoiceNote = generalBilling['generalInvoiceNote']
    except KeyError:
        None

    provider.put()

    return HttpResponse('success')