from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from referal import models

import logging

logger = logging.getLogger(__name__)

def home(request):
	return render_to_response(
		'referal/index.html'
	)

ReferalForm = model_form(models.Referal)

def referalForm(request):
	"""A form function to handle referal form GET and POST requests"""
	form = ReferalForm()
	if request.method == 'POST':
		referal= models.Referal()
		form = ReferalForm(request.POST)
		if form.validate():
			form.populate_obj(referal)
			referal.put()
			logger.info("INFO: successfully stored Referal:" + str(referal))
			return HttpResponseRedirect('/referal')

	return render_to_response(
		'referal/referalform.html',
		{'form': form},
		template.RequestContext(request)
	)
