from common.session import check_session
from common.dwolla import create_account_token
from common.email.login import send_reset_password_email

from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from django.http import HttpResponse

from login import models
from home.models import InitSetupStatus
from parent.models import Parent
from parent import parent_util
from dwollav2.error import ValidationError
from passlib.apps import custom_app_context as pwd_context
from os import environ

import logging

account_token = create_account_token('sandbox')
logger = logging.getLogger(__name__)


def home(request):

    customers = account_token.get('customers')
    logger.info("Customer info: %s" % customers.body['_embedded']['customers'])
    return HttpResponse(customers.body['_embedded']['customers'])

stripFilter = lambda x: x.strip()  if x else ''
ProviderForm = model_form(models.Provider, field_args={
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
        'filters': [stripFilter],
    },
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

LoginForm = model_form(models.Provider, field_args={
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
                request.session['email'] = provider.email
                request.session['user_id'] = provider.key.id()
                request.session['is_provider'] = True
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


                return HttpResponseRedirect('/home/dashboard')
            else:
                form.email.errors.append('error: user exists')

    return render_to_response(
        'login/provider_signup.html',
        {'form': form},
        template.RequestContext(request)
    )


# TODO(zilong): Make sure this won't conflict with the parent data storage in add-child for provider
def parent_signup(request):
    if request.method == 'POST':
        form = ParentForm(request.POST)
        if form.validate():
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone = request.POST.get('phone')
            invitation_token = request.POST.get('invitation_token')

            (parent, created) = get_or_insert(Parent, email, form)
            if created:
                # For Joobali V1, there will be no newly created Parent object at signup
                return None
                create_new_init_setup_status(parent.email)

                request_body = {
                  'firstName': parent.first_name,
                  'lastName': parent.last_name,
                  'email': parent.email,
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
                    pass
                request.session['email'] = parent.email
                request.session['user_id'] = parent.key.id()
                return HttpResponseRedirect('/parent')
            else:
                if not parent_util.verify_invitation_token(email, invitation_token):
                    return HttpResponseRedirect('/login')
                else:
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
                        pass
                    request.session['email'] = parent.email
                    request.session['user_id'] = parent.key.id()

                    return HttpResponseRedirect('/parent')
        else:
            logger.info("form.errors %s" % form.errors)
    elif request.method == 'GET':
        parent_email = request.GET['m']
        invitation_token = request.GET['t']
        if not parent_util.verify_invitation_token(email=parent_email, invitation_token=invitation_token):
            return HttpResponseRedirect('/login')
        parent = parent_util.get_parents_by_email(parent_email)
        provider_school_name = parent.invitation.provider_key.get().schoolName
        child_first_name = parent.invitation.child_first_name
        return render_to_response(
            'login/parent_signup.html',
            {'parent_email': parent_email,
             'invitation_token': invitation_token,
             'child_first_name': child_first_name,
             'provider_school_name' : provider_school_name},
            template.RequestContext(request)
        )


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
            is_provider = True
            query = models.Provider.query().filter(models.Provider.email == email)
            result = query.fetch(1)

            if not result:
                is_provider = False
                query = Parent.query().filter(Parent.email == email)
                result = query.fetch(1)
                if not result:
                    form.email.errors.append('error: user does not exist')
                else:
                    first_name = result[0].first_name
            else:
                first_name = result[0].firstName

            if result:
                emailTemplate = template.loader.get_template('login/forgot_password_email.html')
                data = {
                    'first_name': first_name,
                    'email': email
                }
                send_reset_password_email(first_name, email,
                                    emailTemplate.render(data), "howdy@joobali.com")

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
            result = query.fetch(1)
            if not result:
                is_provider = False
                query = Parent.query().filter(Parent.email == email)
                result = query.fetch(1)
                if not result:
                    form.email.errors.append('error: user does not exist')

            if result and pwd_context.verify(password, result[0].password):
                # authentication succeeded.
                logger.info('login successful')
                request.session['email'] = email
                request.session['user_id'] = result[0].key.id()
                request.session['is_provider'] = is_provider
                request.session['dwolla_customer_url'] = getCustomerUrl(email)
                logger.info('dwolla_customer_url is %s' % request.session['dwolla_customer_url'])
            else:
                form.email.errors.append('error: password wrong')
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