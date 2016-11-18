from common.dwolla import create_account_token
from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from django.http import HttpResponse

from login import models
from gaesessions import get_current_session
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

ParentForm = model_form(models.Parent, field_args={
	'firstName': {
		'filters': [stripFilter],
	},
	'lastName': {
		'filters': [stripFilter],
	},
	'childFirstName': {
		'filters': [stripFilter],
	},
	'childLastName': {
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
	form = ProviderForm()
	if request.method == 'POST':
		form = ProviderForm(request.POST)
		form.validate()
		if form.validate():
			email = request.POST.get('email')
			provider = models.Provider(id=email)
			form.populate_obj(provider)

			provider.password = pwd_context.encrypt(provider.password)

			(provider, created) = get_or_insert(models.Parent, email, provider)
			if created:
				request.session['email'] = provider.email

				request_body = {
				  'firstName': provider.firstName,
				  'lastName': provider.lastName,
				  'email': provider.email,
				  'ipAddress': '99.99.99.99'
				}
				try:
					customer = account_token.post('customers', request_body)
					provider.customerId = customer.headers['location']
					provider.put()
				except ValidationError as err:  # ValidationError as err
					# Do nothing
					pass
				return HttpResponseRedirect('/home/dashboard')
			else:
				form.email.errors.append('error: user exists')


	return render_to_response(
		'login/provider_signup.html',
		{'form': form},
		template.RequestContext(request)
	)

def parent_signup(request):
	form = ParentForm()
	if request.method == 'POST':
		form = ParentForm(request.POST)
		form.validate()
		if form.validate():
			email = request.POST.get('email')
			parent = models.Parent(id=email)
			form.populate_obj(parent)

			parent.password = pwd_context.encrypt(parent.password)

			(parent, created) = get_or_insert(models.Parent, email, parent)
			if created:
				request.session['email'] = parent.email

				request_body = {
				  'firstName': parent.firstName,
				  'lastName': parent.lastName,
				  'email': parent.email,
				  'ipAddress': '99.99.99.99'
				}
				try:
					customer = account_token.post('customers', request_body)
					parent.customerId = customer.headers['location']
					parent.put()
				except ValidationError as err:  # ValidationError as err
					# Do nothing
					print err
					pass
				return HttpResponseRedirect('/home/dashboard')
			else:
				form.email.errors.append('error: user exists')


	return render_to_response(
		'login/parent_signup.html',
		{'form': form},
		template.RequestContext(request)
	)

@ndb.transactional(xg=True)
def get_or_insert(model, email, user):
	result = model.get_by_id(email)
	if result is not None:
		return (result, False)
	user.put()
	logger.info("INFO: successfully stored " + model._get_kind() + ":" + str(user))
	return (user, True)

def login(request):
	form = LoginForm()
	if request.method == 'POST':
		form = LoginForm(request.POST)
		form.validate()
		email = request.POST.get('email')
		password = request.POST.get('password')
		if email and password:
			query = models.Provider.query().filter(models.Provider.email == email)
			result = query.fetch(1)
			if not result:
				query = models.Parent.query().filter(models.Parent.email == email)
				result = query.fetch(1)
				if not result:
					form.email.errors.append('error: user does not exist')


			if result and pwd_context.verify(password, result[0].password):
				# authentication succeeded.
				logger.info('login successful')
				request.session['email'] = email
				request.session['dwolla_customer_url'] = getCustomerUrl(email)
				return HttpResponseRedirect('/home/dashboard')
			else:
				form.email.errors.append('error: password wrong')

	return render_to_response(
		'login/login.html',
		{'form': form},
		template.RequestContext(request)
	)

def getCustomerUrl(email):
	result = models.Provider.get_by_id(email)
	if result is not None:
		return result.customerId
	result = models.Parent.get_by_id(email)
	if result is not None:
		return result.customerId
	raise Exception('user does not exist')

def logout(request):
	loggedIn = False
	if request.session.get('email'):
		loggedIn = True
	if loggedIn:
		request.session.terminate()
	return HttpResponseRedirect('/home')