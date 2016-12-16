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
from parent.models import Parent
from child.models import Child

import json
import logging


logger = logging.getLogger(__name__)


def listInvoices(request):
	"""Handles invoice listing request. Returns invoices associated with the logged in user (provider or parent)"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')
	provider = Provider.get_by_id(email)
    # TODO: handle parent invoice listing.

	invoices = Invoice.query(Invoice.provider_key == provider.key)
	results = []
	for invoice in invoices:
		results.append({
            'provider': invoice.provider_key.get().schoolName,
            'parent': invoice.parent_key.get().email,
            'amount' : invoice.amount
        })
	return HttpResponse(json.dumps(results))