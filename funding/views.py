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
from common.dwolla import list_customers, get_iav_token, remove_funding
from common import dwolla
from dwollav2.error import ValidationError
import json
import logging
from os import environ

logger = logging.getLogger(__name__)

def listFunding(request):
    if not request.session.get('email'):
        return HttpResponseRedirect('/login')
    customer_url = request.session.get('dwolla_customer_url')

    fundings = funding_util.list_fundings(customer_url)
    return HttpResponse(json.dumps([JEncoder().encode(funding) for funding in fundings]))

def listProvider(request):

    customers = list_customers()
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

    customer = get_iav_token(customer_url + '/iav-token')

    return HttpResponse(customer.body['token'])

def makeTransfer(request):

    data = json.loads(request.body)
    invoice_id = data['invoice_id']
    invoice = None
    if invoice_id:
        invoice = Invoice.get_by_id(invoice_id)
        if invoice.amount != data['amount']:
            return HttpResponse("Payment amount must be equal to invoice amount")
        if invoice.is_paid():
            return HttpResponse("The invoice has already been paid")
        if invoice.dwolla_transfer_id and invoice.is_processing():
            return HttpResponse("Payment for this invoice is in process")

    rate = funding_util.get_fee_rate(invoice.provider_key.id())

    try:
        funding_util.make_transfer(data['destination'], data['source'], data['amount'], invoice, rate)
    except ValidationError as err:
        return HttpResponse(err.body['_embedded']['errors'][0]['message'])
    # print transfer.headers['location'] # => 'https://api.dwolla.com/transfers/74c9129b-d14a-e511-80da-0aa34a9b2388'

    return HttpResponse("success")

def verify_micro_deposits(request):

    data = json.loads(request.body)
    funding_url = data['funding_url'] if 'funding_url' in data else None
    first_amount = data['first_amount'] if 'first_amount' in data else None
    second_amount = data['second_amount'] if 'second_amount' in data else None
    if funding_url:
        if first_amount and second_amount:
            try:
                result = dwolla.verify_micro_deposits(funding_url, first_amount, second_amount)
            except ValidationError as err:
                return HttpResponse(err.body['_embedded']['errors'][0]['message'])
        else:
            return HttpResponse("Invalid amount")
    else:
        return HttpResponse("Invalid bank source")

    return HttpResponse("success")

def removeFunding(request):
    data = json.loads(request.body)
    funding_source_id = data['funding_source_id']
    funding_source_url = 'https://%s.dwolla.com/funding-sources/%s' % ('api-sandbox' if environ.get('IS_DEV') == 'True' else 'api', funding_source_id)

    try:
        remove_funding(funding_source_url)
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

    if generalBilling['lateFee']:
        provider.lateFee = float(generalBilling['lateFee'])
    else:
        provider.lateFee = 0

    if generalBilling['graceDays']:
        provider.graceDays = int(generalBilling['graceDays'])
    else:
        provider.graceDays = 0

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