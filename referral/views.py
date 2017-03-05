from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from referral import models
from common.email.referral import send_referral_email
import logging

logger = logging.getLogger(__name__)

def list(request):
	return render_to_response(
		'referral/list.html'
	)

ReferralForm = model_form(models.Referral)

def referralForm(request):
	"""A form function to handle referral form GET and POST requests"""
	form = ReferralForm()
	if request.method == 'POST':
		referral= models.Referral()
		form = ReferralForm(request.POST)
		if form.validate():
			form.populate_obj(referal)
			referral.put()
			logger.info("INFO: successfully stored Referal:" + str(referral))
			emailTemplate = template.loader.get_template('referral/external_referral.html')
			data = {
				'school_name': referral.schoolName
			}
			send_referral_email(referral.schoolName, referral.schoolEmail, referral.referrerName, emailTemplate.render(data))
			logger.info("INFO: successfully sent referral email:" + str(referral))
			return HttpResponseRedirect('/referral')

	return render_to_response(
		'referral/referralform.html',
		{'form': form},
		template.RequestContext(request)
	)
