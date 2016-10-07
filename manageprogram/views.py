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

def edit(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	return render_to_response(
		'manageprogram/edit.html',
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

def listSessions(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	provider = Provider.get_by_id(email)
	# Must specify parent since id is not unique in DataStore
	program = models.Program.get_by_id(int(request.GET.get('id')), parent = provider.key)
	sessions = models.Session.query(ancestor=program.key)

	return HttpResponse(json.dumps([JEncoder().encode(session) for session in sessions]))

def getProgram(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	provider = Provider.get_by_id(email)
	# Must specify parent since id is not unique in DataStore
	program = models.Program.get_by_id(int(request.GET.get('id')), parent = provider.key)
	return HttpResponse(json.dumps([JEncoder().encode(program)]))

def updateProgram(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	newProgram = json.loads(request.body)

	provider = Provider.get_by_id(email)
	# Must specify parent since id is not unique in DataStore
	program = models.Program.get_by_id(int(newProgram['id']), parent = provider.key)


	program.programName = newProgram['programName']

	program.maxCapacity = newProgram['maxCapacity']
	program.registrationFee = newProgram['registrationFee']
	program.fee = newProgram['fee']
	program.feeType = newProgram['feeType']
	program.lateFee = newProgram['lateFee']
	program.billingFrequency = newProgram['billingFrequency']

	program.startDate = datetime.strptime(newProgram['startDate'], '%Y-%m-%d').date()
	program.endDate = datetime.strptime(newProgram['endDate'], '%Y-%m-%d').date()
	program.dueDate = datetime.strptime(newProgram['dueDate'], '%Y-%m-%d').date()
	program.put()

	return HttpResponse('success')

def updateSession(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	data = json.loads(request.body)

	programId = data['programId']

	provider = Provider.get_by_id(email)
	program = models.Program.get_by_id(int(programId), parent = provider.key)

	session = models.Session.get_by_id(int(data['id']), parent = program.key)
	session.sessionName = data['sessionName']
	session.repeatOn = data['repeatOn']
	session.startTime = datetime.strptime(data['startTime'], '%I:%M %p').time()
	session.endTime = datetime.strptime(data['endTime'], '%I:%M %p').time()
	session.put()
	return HttpResponse("success")

def deleteSession(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	data = json.loads(request.body)

	programId = data['programId']

	provider = Provider.get_by_id(email)
	program = models.Program.get_by_id(int(programId), parent = provider.key)

	session = models.Session.get_by_id(int(data['id']), parent = program.key)
	session.key.delete()
	return HttpResponse("success")

def deleteProgram(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	data = json.loads(request.body)

	programId = data['id']

	provider = Provider.get_by_id(email)
	program = models.Program.get_by_id(int(programId), parent = provider.key)

	program.key.delete()
	return HttpResponse("success")

def addProgram(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	data = json.loads(request.body)

	newProgram = data['program']
	sessions = data['sessions']

	provider = Provider.get_by_id(email)
	program = models.Program(parent=provider.key)
	program.programName = newProgram['programName']

	program.maxCapacity = newProgram['maxCapacity']
	program.registrationFee = newProgram['registrationFee']
	program.fee = newProgram['fee']
	program.feeType = newProgram['feeType']
	program.lateFee = newProgram['lateFee']
	program.billingFrequency = newProgram['billingFrequency']

	program.startDate = datetime.strptime(newProgram['startDate'], '%Y-%m-%d').date()
	program.endDate = datetime.strptime(newProgram['endDate'], '%Y-%m-%d').date()
	program.dueDate = datetime.strptime(newProgram['dueDate'], '%Y-%m-%d').date()

	program.put()

	for newSession in sessions:
		session = models.Session(parent=program.key)
		session.sessionName = newSession['sessionName']
		session.repeatOn = newSession['repeatOn']
		session.startTime = datetime.strptime(newSession['startTime'], '%I:%M %p').time()
		session.endTime = datetime.strptime(newSession['endTime'], '%I:%M %p').time()
		session.put()
	return HttpResponse("success")

def addSession(request):
	email = request.session.get('email')
	if not request.session.get('email'):
		return HttpResponseRedirect('/login')

	data = json.loads(request.body)

	print data
	programId = data['programId']

	provider = Provider.get_by_id(email)
	program = models.Program.get_by_id(int(programId), parent = provider.key)

	session = models.Session(parent=program.key)
	session.sessionName = data['sessionName']
	session.repeatOn = data['repeatOn']
	session.startTime = datetime.strptime(data['startTime'], '%I:%M %p').time()
	session.endTime = datetime.strptime(data['endTime'], '%I:%M %p').time()
	session.put()
	return HttpResponse("success")

class JEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ndb.Model):
			result = o.to_dict()
			result['id'] = o.key.id()
			return result
        elif isinstance(o, (datetime, date)):
            return o.isoformat()	  # Or whatever other date format you're OK with...
        elif isinstance(o, time):
            return o.strftime('%I:%M %p')	  # Or whatever other date format you're OK with...