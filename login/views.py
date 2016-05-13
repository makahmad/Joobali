from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form

from login import models

def home(request):
	return render_to_response(
		'login/index.html'
	)

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

def form(request):
	form = ProviderForm()
	if request.method == 'POST':
		provider = models.Provider()
		form = ProviderForm(request.POST)
		print 'FORM:::::::'
		print form.email.errors
		print form.email.filters
		form.validate()
		print 
		if form.validate():
			form.populate_obj(provider)
			query = models.Provider.query().filter(models.Provider.email == provider.email)
			result = query.fetch(1)
			if result:
				form.email.errors.append('error: user exists')
			else:
				provider.put()
				print "INFO: successfully stored Provider:" + str(provider)
				return HttpResponseRedirect('/login')

	return render_to_response(
		'login/userform.html',
		{'form': form},
		template.RequestContext(request)
	)
