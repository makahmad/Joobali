from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
from wtforms_appengine.ndb import model_form
from time import strftime, strptime
from datetime import datetime, date, time
import json

from login.models import Provider

from manageprogram import models


ProgramForm = model_form(models.Program)
SessionForm = model_form(models.Session)

def index(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')
	programForm = ProgramForm()
	sessionForm = SessionForm()
	if request.method == 'POST':
		provider = Provider.get_by_id(email)

		program = models.Program(parent = provider.key)
		session = models.Session()
		programForm = ProgramForm(request.POST)
		sessionForm = SessionForm(request.POST)
		print 'FORM:::::::'
		print request.POST
		print sessionForm.data
		print programForm.data
		repeatOn = ','.join(request.POST.getlist('repeatOn'))
		startTime = request.POST.get('startTime');
		endTime = request.POST.get('endTime');
		if 'startTime' in sessionForm._fields: del sessionForm._fields['startTime']
		if 'endTime' in sessionForm._fields: del sessionForm._fields['endTime']
		if 'repeatOn' in sessionForm._fields: del sessionForm._fields['repeatOn']
		if programForm.validate() and sessionForm.validate():
			programForm.populate_obj(program)
			program.put()
			print "INFO: successfully stored program:" + str(program)
			sessionForm.populate_obj(session)
			session.startTime = datetime.strptime(startTime, '%I:%M %p').time()
			session.endTime = datetime.strptime(endTime, '%I:%M %p').time()
			session.repeatOn = repeatOn
			session.put()
			print "INFO: successfully stored session:" + str(session)
			return HttpResponseRedirect('/manageprogram')
	return render_to_response(
		'manageprogram/index.html',
		{},
		template.RequestContext(request)
	)

def listPrograms(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')
	provider = Provider.get_by_id(email)
	programs = models.Program.query(ancestor=provider.key)
	for program in programs:
		print JEncoder().encode(program)
	return HttpResponse(json.dumps([JEncoder().encode(program) for program in programs]))

class JEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return o.isoformat()	  # Or whatever other date format you're OK with...