from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from django.http import HttpResponse

from login import models
from gaesessions import get_current_session

import dwollav2

def home(request):
	client = dwollav2.Client(id = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9', secret = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9', environment = 'sandbox')
	account_token = client.Token(access_token = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB', refresh_token = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke')

	customers = account_token.get('customers')
	print customers.body['_embedded']['customers']
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

LoginForm = model_form(models.Provider, field_args={
	'email': {
		'filters': [stripFilter],
	},
	'password': {
		'filters': [stripFilter],
	}
})

def signup(request):
	form = ProviderForm()
	if request.method == 'POST':
		provider = models.Provider()
		form = ProviderForm(request.POST)
		print 'FORM:::::::'
		print form.email.errors
		print form.email.filters
		form.validate()
		if form.validate():
			form.populate_obj(provider)
			query = models.Provider.query().filter(models.Provider.email == provider.email)
			result = query.fetch(1)
			if result:
				form.email.errors.append('error: user exists')
			else:
				provider.put()
				request.session['email'] = provider.email
				print "INFO: successfully stored Provider:" + str(provider)


				return HttpResponseRedirect('/home')

	return render_to_response(
		'login/userform.html',
		{'form': form},
		template.RequestContext(request)
	)

def login(request):
	form = LoginForm()
	if request.method == 'POST':
		form = LoginForm(request.POST)
		form.validate()
		email = request.POST.get('email')
		password = request.POST.get('password')
		print 'FORM:::::::'
		print email
		print password
		if email and password:
			print 'haha'
			query = models.Provider.query().filter(models.Provider.email == email)
			result = query.fetch(1)
			print result
			if not result:
				form.email.errors.append('error: user does not exist')
			elif result[0].password == password:
				# authentication succeeded.
				print 'login successful'
				request.session['email'] = email
				print request.session
				return HttpResponseRedirect('/home')
			else:
				form.email.errors.append('error: password wrong')

	return render_to_response(
		'login/login.html',
		{'form': form},
		template.RequestContext(request)
	)

def logout(request):
	loggedIn = False
	if request.session.get('email'):
		loggedIn = True
	if loggedIn:
		request.session.terminate()
	return HttpResponseRedirect('/home')