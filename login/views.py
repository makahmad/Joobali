from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form

from common.session import check_session
from common.dwolla import create_account_token
from common.email.login import send_reset_password_email_for_provider, send_reset_password_email_for_parent, \
    send_provider_email_address_verification

from login import models
from home.models import InitSetupStatus
from login.models import ProviderStatus, Provider
from parent.models import Parent
from parent import parent_util
from verification.models import VerificationToken
from verification import verification_util
from dwollav2.error import ValidationError
from passlib.apps import custom_app_context as pwd_context
from os import environ

import logging

from verification.verification_util import get_parent_signup_verification_token

account_token = create_account_token('sandbox')
logger = logging.getLogger(__name__)


def home(request):
    if request.method == 'GET':
        customers = account_token.get('customers')
        logger.info("Customer info: %s" % customers.body['_embedded']['customers'])
        return HttpResponse(customers.body['_embedded']['customers'])

stripFilter = lambda x: x.strip()  if x else ''
ProviderForm = model_form(models.Provider, exclude=['logo'],field_args={
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


def provider_signup(request):
    logger.info("request.POST %s" % request.POST)
    form = ProviderForm()
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        print form.validate()
        if form.validate():
            email = request.POST.get('email')

            (provider, created) = get_or_insert(models.Provider, email, form)
            if created:
                create_new_init_setup_status(provider.email)

                logger.info("Generating customerId for this provider")
                # Dummy request to dwolla UAT instance to acquire a customer url.
                request_body = {
                    'firstName': provider.firstName,
                    'lastName': provider.lastName,
                    'email': provider.email,
                    'ipAddress': '99.99.99.99'
                }
                try:
                    customer = account_token.post('customers', request_body)
                    logger.info("customer.headers['location'] %s" % customer.headers['location'])
                    provider.customerId = customer.headers['location']
                    provider.put()
                    request.session['dwolla_customer_url'] = customer.headers['location']
                except ValidationError as err:  # ValidationError as err
                    logger.warning(err)
                    # If dwolla customer for this email already exists, reuse it, only in DEV environment.
                    # This shouldn't happen in Prod.
                    if environ.get('IS_DEV') == 'True':
                        if 'Validation' in err.body['code'] and 'Duplicate' in err.body['_embedded']['errors'][0]['code']:
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
                send_provider_email_address_verification(token, host=request.get_host())
                return render_to_response('login/provider_signup_confirmation.html',
                                  {'form': form},
                                  template.RequestContext(request))
                # return HttpResponseRedirect('/login')
            else:
                form.email.errors.append('error: user exists')

    return render_to_response(
        'login/provider_signup.html',
        {'form': form,
         'host': request.get_host()},
        template.RequestContext(request)
    )


def parent_signup(request):
    if request.method == 'GET':
        token_id = request.GET['t']
        verification_token = get_parent_signup_verification_token(token_id)
        if verification_token is not None:
            parent = verification_token.parent_key.get()
            provider_school_name = parent.invitation.provider_key.get().schoolName
            child_first_name = parent.invitation.child_first_name
            return render_to_response(
                'login/parent_signup.html',
                {'parent_email': parent.email,
                 'invitation_token': token_id,
                 'child_first_name': child_first_name,
                 'provider_school_name' : provider_school_name},
                template.RequestContext(request)
            )
        else:
            return HttpResponse("Need a valid token id for parent to signup")
    if request.method == 'POST':
        form = ParentForm(request.POST)
        if form.validate():
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            token_id = request.POST.get('invitation_token')
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
                                                           first_name=first_name, last_name=last_name)
                request.session['email'] = parent.email
                request.session['user_id'] = parent.key.id()
                request.session['is_provider'] = False

                # Setup Dwolla Account
                request_body = {
                    'firstName': first_name,
                    'lastName': last_name,
                    'email': email,
                    'ipAddress': '99.99.99.99'
                }
                try:
                    customer = account_token.post('customers', request_body)
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
            logger.info("form.errors %s" % form.errors)


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
def get_or_insert(model, email, form):
    result = models.Unique.get_by_id(email)
    if result is not None:
        return result, False

    user = model(id=model.get_next_available_id())
    form.populate_obj(user)

    user.password = pwd_context.encrypt(user.password)
    user.put()
    unique = models.Unique(id=email)
    if model._get_kind() == "Provider":
        unique.provider_key = user.key
    else:
        unique.parent_key = user.key
    unique.put()
    logger.info("INFO: successfully stored " + model._get_kind() + ":" + str(user))
    return user, True


def forgot(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.validate()
        email = request.POST.get('email')

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
                send_reset_password_email_for_provider(token, request.get_host())
            elif parent_result:
                token = VerificationToken.create_new_parent_password_reset_token(parent_result[0])
                token.put()
                send_reset_password_email_for_parent(token, request.get_host())

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
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            is_provider = True
            query = models.Provider.query().filter(models.Provider.email == email)
            result = query.get()
            if not result:
                is_provider = False
                query = Parent.query().filter(Parent.email == email)
                result = query.get()
                if not result:
                    logger.info('Error: wrong combination of credential');
                    form.email.errors = 'Error: wrong combination of credential'
                    return render_to_response(
                        'login/login.html',
                        {'form': form},
                        template.RequestContext(request))
            if isinstance(result, Provider):
                if result.status.status != 'active':
                    logger.info('Error: user has not yet verify email');
                    form.email.errors = 'Error: user has not yet verify email'
                    return render_to_response(
                        'login/login.html',
                        {'form': form},
                        template.RequestContext(request))

            if result and pwd_context.verify(password, result.password):
                # authentication succeeded.
                logger.info('login successful')
                request.session['email'] = email
                request.session['user_id'] = result.key.id()
                request.session['is_provider'] = is_provider
                request.session['dwolla_customer_url'] = getCustomerUrl(email)
                logger.info('dwolla_customer_url is %s' % request.session['dwolla_customer_url'])
            else:
                form.email.errors = 'Error: wrong combination of credential'
    if check_session(request):
        if request.session.get('is_provider') is True:
            return HttpResponseRedirect("/home/dashboard")
        else:
            return HttpResponseRedirect("/parent")
    return render_to_response(
        'login/login.html',
        {'form': form},
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