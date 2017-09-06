from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form

from common.email.enrollment import send_parent_enrollment_notify_email
from common.session import check_session, is_provider, is_parent
from common.dwolla import create_customer
from common.email.login import send_reset_password_email_for_provider, send_reset_password_email_for_parent, \
    send_provider_email_address_verification

from login import models
from common.request import get_host_from_request
from home.models import InitSetupStatus
from login.login_util import provider_login, parent_login
from login.models import ProviderStatus, Provider, FailedBetaLogins
from parent.models import Parent
from parent import parent_util
from parent.parent_util import get_parents_by_email
from verification.models import VerificationToken
from verification import verification_util
from dwollav2.error import ValidationError
from passlib.apps import custom_app_context as pwd_context
from os import environ

import logging
from jose import jwt
from datetime import datetime
import random
import urllib, urllib2, json
from verification.verification_util import get_parent_signup_verification_token

DATE_FORMAT = '%m/%d/%Y'

logger = logging.getLogger(__name__)

stripFilter = lambda x: x.strip() if x else ''
ProviderForm = model_form(models.Provider, exclude=['logo', 'doc'], field_args={
    'firstName': {
        'filters': [stripFilter],
    },
    'lastName': {
        'filters': [stripFilter],
    },
    'schoolName': {
        'filters': [stripFilter],
    },
    'email': {
        'filters': [stripFilter],
    },
    'password': {
        'filters': [stripFilter],
    },
    'phone': {
        'filters': [stripFilter],
    },
    'license': {
        'filters': [stripFilter]
    }
})

ParentForm = model_form(Parent, field_args={
    'first_name': {
        'filters': [stripFilter],
    },
    'last_name': {
        'filters': [stripFilter],
    },
    'email': {
        'filters': [stripFilter],
    },
    'password': {
        'filters': [stripFilter],
    },
})

LoginForm = model_form(models.Provider, only={
    'email': {
        'filters': [stripFilter],
    },
    'password': {
        'filters': [stripFilter],
    }
})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def provider_signup(request):
    # If the user is logged in, redirect them to the dashboard / parent page
    if check_session(request):
        if is_provider(request):
            return HttpResponseRedirect("/home/dashboard")
        elif is_parent(request):
            return HttpResponseRedirect("/parent")

    logger.info("request.POST %s" % request.POST)
    form = ProviderForm()
    captcha_results = dict()
    captcha_results['success'] = False

    if request.method == 'POST':
        form = ProviderForm(request.POST)

        captcha_rs = request.POST.get('g-recaptcha-response')
        if captcha_rs:
            url = "https://www.google.com/recaptcha/api/siteverify"
            params = [('secret', '6Lf6Gh8UAAAAANJcx3uuFdc_1a4pEtr-bdqO0Hs3'), ('response', captcha_rs),
                      ('remoteip', get_client_ip(request))]
            result = urllib2.urlopen(url, urllib.urlencode(params))
            captcha_results = json.load(result)
        else:
            captcha_results['success'] = True

        # Remove below snippet once we are out of Beta
        beta_code = request.POST.get('beta_code')
        if beta_code != 'joobali143':
            failedBetaLogins = FailedBetaLogins()
            failedBetaLogins.IP = get_client_ip(request)
            failedBetaLogins.email = request.POST.get('email')
            failedBetaLogins.firstName = request.POST.get('firstName')
            failedBetaLogins.schoolName = request.POST.get('schoolName')
            failedBetaLogins.lastName = request.POST.get('lastName')
            failedBetaLogins.phone = request.POST.get('phone')
            failedBetaLogins.license = request.POST.get('license')
            failedBetaLogins.date = datetime.now()
            failedBetaLogins.beta_code = request.POST.get('beta_code')
            failedBetaLogins.put()

            return render_to_response(
                'login/provider_signup.html',
                {'form': form,
                 'host': get_host_from_request(request.get_host()),
                 'captcha': captcha_results['success'],
                 'beta_error': True,
                 'home_url': 'https://www.joobali.com'},
                template.RequestContext(request)
            )
        # Remove above snippet once we are out of Beta

        if form.validate() and captcha_results['success']:
            email = request.POST.get('email').lower()

            (provider, created) = get_or_insert(email, form)
            if created:
                create_new_init_setup_status(provider.email)

                logger.info("Generating customerId for this provider")
                # Dummy request to dwolla UAT instance to acquire a customer url.
                request_body = {
                    'firstName': provider.firstName,
                    'lastName': provider.lastName,
                    'email': provider.email,
                    'ipAddress': get_client_ip(request),
                }
                try:
                    customer = create_customer(request_body)
                    logger.info("customer.headers['location'] %s" % customer.headers['location'])
                    provider.customerId = customer.headers['location']
                    provider.put()
                    request.session['dwolla_customer_url'] = customer.headers['location']
                except ValidationError as err:  # ValidationError as err
                    logger.warning(err)
                    # If dwolla customer for this email already exists, reuse it, only in DEV environment.
                    # This shouldn't happen in Prod.
                    if environ.get('IS_DEV') == 'True':
                        if 'Validation' in err.body['code'] and 'Duplicate' in err.body['_embedded']['errors'][0][
                            'code']:
                            provider.customerId = err.body['_embedded']['errors'][0]['_links']['about']['href']
                            request.session['dwolla_customer_url'] = provider.customerId
                            provider.put()
                    pass
                provider_status = ProviderStatus()
                provider_status.status = 'signup'
                provider.status = provider_status
                provider.put()
                token = VerificationToken.create_new_provider_email_token(provider=provider)
                token.put()
                send_provider_email_address_verification(token, host=get_host_from_request(request.get_host()))
                return render_to_response('login/provider_signup_confirmation.html',
                                          {'form': form,
                                           'email': email,
		                                   'home_url': 'https://www.joobali.com'},
                                          template.RequestContext(request))
                # return HttpResponseRedirect('/login')
            else:
                form.email.errors.append('error: user exists')

    return render_to_response(
        'login/provider_signup.html',
        {'form': form,
         'host': get_host_from_request(request.get_host()),
         'captcha': captcha_results['success'],
		  'home_url': 'https://www.joobali.com'},
        template.RequestContext(request)
    )


def parent_signup(request):
    # If the parent is logged in, redirect them to their dashboard
    if request.session.get('email'):
        return HttpResponseRedirect("/parent")

    if request.method == 'GET':
        if 't' in request.GET:
            token_id = request.GET['t']
            verification_token = get_parent_signup_verification_token(token_id)
            if verification_token is not None:
                parent = verification_token.parent_key.get()
                provider_school_name = parent.invitation.provider_key.get().schoolName
                child_first_name = parent.invitation.child_first_name

                child_dob = parent.invitation.enrollment_key.get().child_key.get().date_of_birth
                if child_dob:
                    child_dob = child_dob.strftime('%m/%d/%Y')
                else:
                    child_dob = ''

                return render_to_response(
                    'login/parent_signup.html',
                    {'parent_email': parent.email,
                     'invitation_token': token_id,
                     'child_first_name': child_first_name,
                     'child_dob': child_dob,
                     'provider_school_name': provider_school_name,
                     'home_url': 'https://www.joobali.com'},
                    template.RequestContext(request)
                )
        return render_to_response('login/parent_proactive_signup.html',
                                  {'submitted': False,
                                   'errors': False},
                                  template.RequestContext(request))

    if request.method == 'POST':
        form = ParentForm(request.POST)

        if form.validate():
            email = request.POST.get('email').lower()
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            token_id = request.POST.get('invitation_token')
            child_date_of_birth = request.POST.get('child_date_of_birth')
            tos_pp_accepted = request.POST.get('tos_pp_accepted') == 'on'

            verification_token = get_parent_signup_verification_token(token_id)

            if verification_token is None:
                logger.info("verification_token %s id is invalid" % token_id)
                return HttpResponseRedirect('/login')
            else:
                parent = verification_token.parent_key.get()
                create_new_init_setup_status(parent.email)
                salted_password = pwd_context.encrypt(password)
                parent = parent_util.signup_invited_parent(email=email, salted_password=salted_password,
                                                           phone=phone,
                                                           first_name=first_name, last_name=last_name, tos_pp_accepted=tos_pp_accepted)

                child = parent.invitation.enrollment_key.get().child_key.get()
                child.date_of_birth = datetime.strptime(child_date_of_birth, DATE_FORMAT).date()
                child.put()

                request.session['email'] = parent.email
                request.session['user_id'] = parent.key.id()
                request.session['is_provider'] = False

                # Setup Dwolla Account
                request_body = {
                    'firstName': first_name,
                    'lastName': last_name,
                    'email': email,
                    'ipAddress': get_client_ip(request),
                }
                try:
                    customer = create_customer(request_body)
                    parent.customerId = customer.headers['location']
                    parent.put()
                    request.session['dwolla_customer_url'] = customer.headers['location']
                    request.session['parent_id'] = parent.key.id()
                except ValidationError as err:  # ValidationError as err
                    if environ.get('IS_DEV') == 'True':
                        # If dwolla customer for this email already exists, reuse it, only in DEV environment.
                        # This shouldn't happen in Prod.
                        if 'Validation' in err.body['code'] and 'Duplicate' in err.body['_embedded']['errors'][0][
                            'code']:
                            parent.customerId = err.body['_embedded']['errors'][0]['_links']['about']['href']
                            request.session['dwolla_customer_url'] = parent.customerId
                            parent.put()

                # Configs HTTP Session for client
                request.session['email'] = parent.email
                request.session['user_id'] = parent.key.id()
                verification_token.key.delete()
                return HttpResponseRedirect('/parent')
        else:
            if 'email' in request.POST:
                email = request.POST.get('email').lower()
                parent = get_parents_by_email(email)
                if parent is not None:
                    if parent.invitation is not None:
                        if parent.invitation.enrollment_key is not None:
                            if parent.status.status != 'active':
                                send_parent_enrollment_notify_email(parent.invitation.enrollment_key.get(),
                                                                    get_host_from_request(
                                                                        request_host=request.get_host()))
                                return render_to_response('login/parent_proactive_signup.html',
                                                          {'submitted': True,
                                                    'errors': False},
                                                   template.RequestContext(request))
                            else:
                                errors = ("parent %s is already active, no need to signup again" % email)
                        else:
                            errors = ("parent %s does not have an invitation" % email)
                    else:
                        errors = ("parent %s is not invited anymore" % email)
                else:
                    errors = ("parent %s is not found" % email)
            else:
                errors = "invalid request"
            return render_to_response('login/parent_proactive_signup.html',
                                      {'submitted': False,
                                       'errors': errors},
                                      template.RequestContext(request))




def create_new_init_setup_status(email):
    ''' Create a new InitSetupStatus object with unfinished status '''
    initSetupStatus = InitSetupStatus(id=email)
    initSetupStatus.email = email
    initSetupStatus.setupFinished = False
    initSetupStatus.put()


def is_init_setup_finished(request):
    ''' If the user is just signed up. For deciding the display of init setup flow'''
    result = InitSetupStatus.get_by_id(request.session['email'])
    if (result is not None) and result.setupFinished == True:
        return HttpResponse('true');
    return HttpResponse('false');


@ndb.transactional(xg=True)
def set_init_setup_finished(request):
    ''' Set true that the init setup status is finished '''
    email = request.session['email']
    result = InitSetupStatus.get_by_id(email)
    if result is None:
        initSetupStatus = InitSetupStatus(id=email)
        initSetupStatus.email = email
        initSetupStatus.setupFinished = True
        initSetupStatus.put()
    else:
        result.setupFinished = True
        result.put();
    return HttpResponse('success');


@ndb.transactional(xg=True)
def get_or_insert(email, form):
    email = email.lower()
    result = models.Unique.get_by_id(email)
    if result is not None:
        return result, False

    provider = Provider(id=Provider.get_next_available_id())
    form.populate_obj(provider)

    provider.password = pwd_context.encrypt(provider.password)
    provider.put()
    unique = models.Unique(id=email)
    unique.provider_key = provider.key
    unique.put()
    logger.info("INFO: successfully stored Provider :" + str(provider))
    return provider, True


def forgot(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.validate()
        email = request.POST.get('email').lower()

        if email:
            query = models.Provider.query().filter(models.Provider.email == email)
            provider_result = query.fetch(1)
            parent_result = None

            if not provider_result:
                query = Parent.query().filter(Parent.email == email)
                parent_result = query.fetch(1)
                if not parent_result:
                    form.email.errors.append('error: user does not exist')

            if provider_result:
                token = VerificationToken.create_new_provider_password_reset_token(provider_result[0])
                token.put()
                send_reset_password_email_for_provider(token, get_host_from_request(request.get_host()))
            elif parent_result:
                token = VerificationToken.create_new_parent_password_reset_token(parent_result[0])
                token.put()
                send_reset_password_email_for_parent(token, get_host_from_request(request.get_host()))

            if provider_result or parent_result:
                return render_to_response('login/forgot_sent.html',
                                          {'form': form},
                                          template.RequestContext(request))

    if check_session(request):
        if request.session.get('is_provider') is True:
            return HttpResponseRedirect("/home/dashboard")
        else:
            return HttpResponseRedirect("/parent")

    return render_to_response(
        'login/forgot.html',
        {'form': form},
        template.RequestContext(request))


def reset(request):
    if request.method == 'GET':
        token_id = request.GET['t']
        token = verification_util.get_password_reset_token(token_id)
        if token is not None:
            form = dict()
            form['token'] = token.token_id
            if token.provider_key is not None:
                provider = token.provider_key.get()
                form['first_name'] = provider.firstName
                form['email_address'] = provider.email
            elif token.parent_key is not None:
                parent = token.parent_key.get()
                form['first_name'] = parent.first_name
                form['email_address'] = parent.email
            else:
                return HttpResponseRedirect("/login")
            return render_to_response(
                'login/reset_password.html',
                {'form': form},
                template.RequestContext(request))

    if request.method == 'POST':
        token_id = request.POST.get('token')
        token = verification_util.get_password_reset_token(token_id)
        if token is not None:
            password = request.POST.get('password')
            salted_password = pwd_context.encrypt(password)
            if token.provider_key is not None:
                provider = token.provider_key.get()
                provider.password = salted_password
                provider.put()
            elif token.parent_key is not None:
                parent = token.parent_key.get()
                parent.password = salted_password
                parent.put()
            token.key.delete()
            return render_to_response('login/reset_done.html', None,
                                      template.RequestContext(request))

    if check_session(request):
        if request.session.get('is_provider') is True:
            return HttpResponseRedirect("/home/dashboard")
        else:
            return HttpResponseRedirect("/parent")

    return HttpResponseRedirect("/login")


def login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.validate()
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        login_result = provider_login(email, password)
        if login_result.is_succeeded() is False:
            login_result = parent_login(email, password)
        if login_result.is_succeeded():
            # authentication succeeded.
            logger.info('login successful')
            request.session['email'] = login_result.email
            request.session['name'] = login_result.name
            request.session['user_id'] = login_result.user_id
            request.session['is_provider'] = login_result.is_provider
            request.session['dwolla_customer_url'] = login_result.dwolla_customer_url
            request.session['is_admin'] = False

            if email == 'joobali-prod@joobali.com':
                request.session['is_admin'] = True

            logger.info('dwolla_customer_url is %s' % request.session['dwolla_customer_url'])
        else:
            form.email.errors = login_result.error_msg

    redirect = ''
    if request.POST.get('url') and '#!' in request.POST.get('url'):
        redirect = '/#!' + request.POST.get('url').split('#!')[1]
    return_to = request.GET.get('return_to')

    if return_to == 'None':
        return_to = None

    zendesk = request.GET.get('z')
    if zendesk == 'None':
        zendesk = None

    if check_session(request) and not zendesk:
        if request.session.get('is_provider') is True:
            return HttpResponseRedirect("/home/dashboard"+redirect)
        else:
            return HttpResponseRedirect("/parent"+redirect)
    elif check_session(request) and zendesk:
        payload = {
            'name': request.session.get('name'),
            'email': request.session.get('email'),
            'iat': datetime.now(),
            'jti': request.session.get('email') + str(random.getrandbits(64))
        }
        if request.session.get('is_provider') is True:
            payload['user_fields'] = {'is_provider_': True}
        else:
            payload['user_fields'] = {'is_parent_': True}

        shared_key = 'X837bnHY15qx7iLf9uYOmNVWXNW77wCoQKctGajLN1NboEy5'
        jwt_string = jwt.encode(payload, shared_key)
        location = "https://joobali.zendesk.com/access/jwt?jwt=" + jwt_string

        if return_to is not None:
            location += "&return_to=" + urllib.quote(return_to)

        return HttpResponseRedirect(location)

    return render_to_response(
        'login/login.html',
        {'form': form,
         'return_to': return_to,
         'z': zendesk},
        template.RequestContext(request))


def getCustomerUrl(email):
    result = models.Provider.query().filter(models.Provider.email == email)
    if result.fetch(1):
        return result.fetch(1)[0].customerId

    result = parent_util.get_parents_by_email(email)
    if result is not None:
        return result.customerId

    raise Exception('user does not exist')


def logout(request):
    loggedIn = False
    if request.session.get('email'):
        loggedIn = True
    if loggedIn:
        request.session.terminate()
    return HttpResponseRedirect('/login')


def terms_of_service(request):
    return render_to_response(
        'login/docs/terms_of_service.html')


def privacy_policy(request):
    return render_to_response(
        'login/docs/privacy_policy.html')
