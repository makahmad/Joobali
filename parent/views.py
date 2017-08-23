from common.json_encoder import JEncoder
from common.session import check_session
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import template
from passlib.apps import custom_app_context as pwd_context
from common.email.referral import send_parent_referral_email
from models import Parent
from referral import models
from child import child_util
from enrollment import enrollment_util
from child.models import ProviderChildView
from funding import funding_util
from django.http import HttpResponse
import logging
import json
from jose import jwt
from datetime import datetime
import random
from login import unique_util
from google.appengine.ext import ndb

logger = logging.getLogger(__name__)


def care(request):

    return render_to_response(
        'parent/care.html',
        {
            'loggedIn': check_session(request),
            'email': request.session.get('email'),
            'home_url': 'https://www.joobali.com'
        },
        template.RequestContext(request)
    )


def index(request):
    if not check_session(request) or request.session['is_provider'] is True:
        return HttpResponseRedirect('/login')

    payload = {
        'name': request.session.get('name'),
        'email': request.session.get('email'),
        'iat': datetime.now(),
        'jti': request.session.get('email') + str(random.getrandbits(64))
    }
    zendesk_token = jwt.encode(payload, '06d401e8e50ac108d2da325caa12854c')

    return render_to_response(
        'parent/index.html',
        {
            'loggedIn': True,
            'email': request.session.get('email'),
			'zendesk_token': zendesk_token,
			'name': request.session.get('name')
        },
        template.RequestContext(request)
    )


def getProfile(request):
    """Handles get profile request. Returns the profile with provided email"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if request.session['is_provider']:
        return HttpResponseRedirect('/login')

    parent = Parent.get_by_id(request.session['user_id'])
    if parent is not None:
        return HttpResponse(json.dumps([JEncoder().encode(parent)]))

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))


def updateProfile(request):
    """Updates the program with provided program ID"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if request.session['is_provider']:
        return HttpResponseRedirect('/login')

    profile = json.loads(request.body)

    if not profile['id']:
        raise Exception('no profile id is provided')

    # provider profile update
    parent = Parent.get_by_id(request.session['user_id'])

    if request.session['email'] != profile['email'].lower():
        query = Parent.query().filter(Parent.email == profile['email'].lower())
        result = query.fetch(1)
        if result:
            return HttpResponseServerError('email already exists')
        request.session['email'] = profile['email'].lower()

    if parent is not None:
        if 'currentPassword' in profile and 'newPassword' in profile:
            if pwd_context.verify(profile['currentPassword'], parent.password):
                parent.password = pwd_context.encrypt(profile['newPassword'])
            else:
                return HttpResponseServerError('current password is incorrect')
        parent.first_name = profile['first_name']
        parent.last_name = profile['last_name']

        unique_util.update_parent(parent.email, profile['email'].lower(), parent.key)
        parent.email = profile['email'].lower()
        parent.phone = profile['phone']
        parent.put()

    return HttpResponse('success')


def validateEmail(request):
    """Validates user email. Successful if email does not already exist in the system, otherwise failure"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    email = json.loads(request.body)

    parent = Parent.get_by_id(request.session['user_id'])

    if request.session['email'] != email:
        if not request.session['is_provider']:
            query = Parent.query().filter(Parent.email == email)
            result = query.fetch(1)
            if result:
                return HttpResponseServerError('failure')

    return HttpResponse('success')


def get_autopay_data(request):
    if not check_session(request):
        return HttpResponseRedirect('/login')

    parent = Parent.get_by_id(request.session['user_id'])
    enrollment = parent.invitation.enrollment_key.get()
    provider = enrollment.key.parent().get()
    child = enrollment.child_key.get()
    program = enrollment.program_key.get()
    due_date = enrollment.start_date

    due_date_text = ''
    if program.billingFrequency == 'Monthly':
        number_th = 'th'
        number_day = due_date.day
        if number_day == 1:
            number_th = 'st'
        elif number_day == 2:
            number_th = 'nd'
        elif number_day == 3:
            number_th = 'rd'
        due_date_text = '%s%s of the %s' % (number_day, number_th, program.billingFrequency[:-2])
    elif program.billingFrequency == 'Weekly':
        due_date_text = 'Every %s' % due_date.strftime('%A')
    data = {
        'providerName': provider.schoolName,
        'programName': program.programName,
        'childFirstName': child.first_name,
        'paymentAmount': '%s / %s' % (enrollment.billing_fee if enrollment.billing_fee else program.fee, program.billingFrequency[:-2]),
        'billingFrequency': program.billingFrequency,
        'dueDate': due_date_text,
        'bankAccounts': funding_util.list_fundings(request.session['dwolla_customer_url'])
    }

    return HttpResponse(json.dumps([JEncoder().encode(data)]))

def parentReferral(request):
    """A form function to handle internal referral form POST requests"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if request.session['is_provider']:
        return HttpResponseRedirect('/login')

    response = dict()

    if request.method != 'POST':
        logger.info('request.method is %s', request.method)
        response['status'] = 'failure'
    else:
        referralForm = json.loads(request.body)
        parent = Parent.get_by_id(request.session['user_id'])

        referral = models.Referral()
        referral.schoolName = referralForm['schoolName']
        referral.referrerName = parent.firstName+" "+parent.lastName
        referral.referrerEmail = parent.email
        referral.schoolEmail = referralForm['email']
        referral.schoolPhone = referralForm['phone']
        referral.put()

        emailTemplate = template.loader.get_template('referral/external_referral.html')
        data = {
            'school_name': referralForm['schoolName'],
            'referrer_name': referral.referrerName
        }
        send_parent_referral_email(referral.schoolName, referral.schoolEmail, referral.referrerName,
                            emailTemplate.render(data), "Joobali <howdy@joobali.com>")
        response['status'] = 'success'
    return HttpResponse(json.dumps(response), content_type="application/json")


def has_enrollment(request):
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if request.session['is_provider']:
        return HttpResponseRedirect('/login')

    has_enrollment = False

    parent_id = request.session['user_id']

    parent_key = Parent.generate_key(parent_id)
    children = child_util.list_child_by_parent(parent_key=parent_key)
    for child in children:

        if parent_key != child.parent_key:
            return
        provider_child_view_query = ProviderChildView.query_by_child_id(child.key.id())

        enrollments = list()
        for provider_child_view in provider_child_view_query:
            provider_key = provider_child_view.provider_key
            child_key = provider_child_view.child_key
            enrollments += enrollment_util.list_enrollment_by_provider_and_child(provider_key=provider_key,
                                                                                 child_key=child_key)
            for enrollment in enrollments:
                if enrollment.status == 'active':
                    has_enrollment = True

    return HttpResponse(json.dumps(has_enrollment), content_type="application/json")