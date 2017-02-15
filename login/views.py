from common.session import check_session
from common.dwolla import create_account_token
from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from django.http import HttpResponse

from login import models
from home.models import InitSetupStatus
from parent.models import Parent
from dwollav2.error import ValidationError
from passlib.apps import custom_app_context as pwd_context

import dwollav2
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
            provider = models.Provider()
            form.populate_obj(provider)

            provider.password = pwd_context.encrypt(provider.password)

            (provider, created) = get_or_insert(models.Provider, email, provider)
            if created:
                logger.info("Generating customerId for this provider")
                request.session['email'] = provider.email
                create_new_init_setup_status(provider.email)

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
                    request.session['user_id'] = provider.key.id()
                except ValidationError as err:  # ValidationError as err
                    # Do nothing
                    logger.warning(err)
                    pass
                return HttpResponseRedirect('/home/dashboard')
            else:
                form.email.errors.append('error: user exists')

    return render_to_response(
        'login/provider_signup.html',
        {'form': form},
        template.RequestContext(request)
    )


# TODO(zilong): Make sure this won't conflict with the parent data storage
# in add-child for provider
def parent_signup(request):
    form = ParentForm()
    if request.method == 'POST':
        form = ParentForm(request.POST)
        form.validate()
        if form.validate():
            email = request.POST.get('email')
            parent = Parent(id=email)
            form.populate_obj(parent)

            parent.password = pwd_context.encrypt(parent.password)

            (parent, created) = get_or_insert(Parent, email, parent)
            if created:
                request.session['email'] = parent.email
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
                    # Do nothing
                    print err
                    pass
                return HttpResponseRedirect('/parent')
            else:
                form.email.errors.append('error: user exists')
    else:
        form.email.data = request.GET.get('email', '')
    return render_to_response(
        'login/parent_signup.html',
        {'form': form},
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
def get_or_insert(model, email, user):
    result = model.get_by_id(email)
    if result is not None:
        return result, False
    user.put()
    logger.info("INFO: successfully stored " + model._get_kind() + ":" + str(user))
    return user, True


# TODO(zilong): Allow parent login
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
    result = Parent.get_by_id(email)
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