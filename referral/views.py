import json
from django.shortcuts import render_to_response
from common.session import check_session
from django import template
from django.http import HttpResponseRedirect,HttpResponse
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from referral import models
from common.email.referral import send_referral_email,send_provider_referral_email
import logging
from login.models import Provider

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
        referral = models.Referral()
        form = ReferralForm(request.POST)
        if form.validate():
            form.populate_obj(referral)
            referral.put()
            logger.info("INFO: successfully stored Referral:" + str(referral))
            emailTemplate = template.loader.get_template('referral/external_referral.html')
            data = {
                'school_name': referral.schoolName,
                'referrer_name': referral.referrerName
            }
            send_referral_email(referral.schoolName, referral.schoolEmail, referral.referrerName,
                                emailTemplate.render(data), "rongjian@joobali.com")
            logger.info("INFO: successfully sent referral email:" + str(referral))
            return HttpResponseRedirect('/referral')

    return render_to_response(
        'referral/referralform.html',
        {'form': form},
        template.RequestContext(request)
    )


def providerReferral(request):
    """A form function to handle internal referral form POST requests"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if not request.session['is_provider']:
        return HttpResponseRedirect('/login')

    response = dict()

    if request.method != 'POST':
        logger.info('request.method is %s', request.method)
        response['status'] = 'failure'
    else:
        referralForm = json.loads(request.body)
        provider = Provider.get_by_id(request.session['user_id'])

        referral = models.Referral()
        referral.schoolName = referralForm['schoolName']
        referral.referrerName = provider.firstName+" "+provider.lastName
        referral.referrerEmail = provider.email
        referral.schoolEmail = referralForm['email']
        referral.schoolPhone = referralForm['phone']
        referral.put()

        emailTemplate = template.loader.get_template('referral/external_referral.html')
        data = {
            'school_name': referralForm['schoolName'],
            'referrer_name': referral.referrerName
        }
        send_provider_referral_email(referral.schoolName, referral.schoolEmail, referral.referrerName,
                            emailTemplate.render(data), "rongjian@joobali.com")
        response['status'] = 'success'
    return HttpResponse(json.dumps(response), content_type="application/json")