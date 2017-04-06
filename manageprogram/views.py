from common.json_encoder import JEncoder
from common.session import check_session
from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from datetime import datetime
from child import child_util
from child.models import Child
from enrollment import enrollment_util
from login.models import Provider
from manageprogram import models
from manageprogram import program_util

import json
import logging

logger = logging.getLogger(__name__)

DATE_FORMAT = '%m/%d/%Y'

def index(request):
    """Handles the landing page request for program management page"""
    email = request.session.get('email')
    if not check_session(request):
        return HttpResponseRedirect('/login')

    return render_to_response(
        'manageprogram/index.html',
        {},
        template.RequestContext(request)
    )

def edit(request):
    """Handles the program editing page request"""
    email = request.session.get('email')
    if not check_session(request):
        return HttpResponseRedirect('/login')

    return render_to_response(
        'manageprogram/edit.html',
        {},
        template.RequestContext(request)
    )


def listPrograms(request):
    """Handles program listing request. Returns programs associated with the logged in user"""
    user_id = request.session.get('user_id')
    if not check_session(request):
        return HttpResponseRedirect('/login')
    programs = program_util.list_program_by_provider_user_id(user_id)
    output = list()
    for program in programs:
        logger.info("program %s" % program)
        logger.info("JEncoder().encode(program) %s" % JEncoder().encode(program))
        output.append(program)
    return HttpResponse(json.dumps([JEncoder().encode(program) for program in output]),
                        content_type="application/json")


def getProgram(request):
    """Handles get program request. Returns the program with provided program ID"""
    user_id = request.session.get('user_id')
    if not check_session(request):
        return HttpResponseRedirect('/login')
    if not request.GET.get('id'):
        raise Exception('no program id is provided')

    provider = Provider.get_by_id(user_id)
    # Must specify parent since id is not unique in DataStore
    program = models.Program.get_by_id(int(request.GET.get('id')), parent = provider.key)
    return HttpResponse(json.dumps([JEncoder().encode(program)]), content_type="application/json")

def getDefaultLateFee(request):
    """Handles get program request. Returns the program with provided program ID"""
    user_id = request.session.get('user_id')
    if not check_session(request):
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(user_id)
    return HttpResponse(provider.lateFee)

def updateProgram(request):
    """Updates the program with provided program ID"""
    user_id = request.session.get('user_id')
    if not check_session(request):
        return HttpResponseRedirect('/login')

    newProgram = json.loads(request.body)

    if not newProgram['id']:
        raise Exception('no program id is provided')

    provider = Provider.get_by_id(user_id)
    # Must specify parent since id is not unique in DataStore
    program = models.Program.get_by_id(int(newProgram['id']), parent = provider.key)


    program.programName = newProgram['programName']

    # program.maxCapacity = newProgram['maxCapacity']
    # program.registrationFee = newProgram['registrationFee']
    # program.fee = newProgram['fee']
    # program.feeType = newProgram['feeType']
    # program.lateFee = newProgram['lateFee']
    # program.billingFrequency = newProgram['billingFrequency']

    program.startDate = datetime.strptime(newProgram['startDate'], DATE_FORMAT).date()

    if newProgram['indefinite']:
        program.indefinite = newProgram['indefinite']
        program.endDate = None
    else:
        program.endDate = datetime.strptime(newProgram['endDate'], DATE_FORMAT).date()

    # program.dueDate = datetime.strptime(newProgram['dueDate'], DATE_FORMAT).date()
    program.put()

    return HttpResponse('success')

def deleteProgram(request):
    """Deletes the program with provided program ID"""
    user_id = request.session.get('user_id')
    if not check_session(request):
        return HttpResponseRedirect('/login')

    data = json.loads(request.body)

    programId = data['id']
    if not programId:
        raise Exception('no program id is provided')

    provider = Provider.get_by_id(user_id)
    program = models.Program.get_by_id(int(programId), parent = provider.key)

    program.key.delete()
    return HttpResponse("success")

def addProgram(request):
    """Adds a new program along with associated sessions to the logged in user"""
    user_id = request.session.get('user_id')
    if not check_session(request):
        return HttpResponseRedirect('/login')

    data = json.loads(request.body)

    newProgram = data['program']

    provider = Provider.get_by_id(user_id)
    program = models.Program(parent=provider.key)
    program.programName = newProgram['programName']

    program.registrationFee = newProgram['registrationFee']
    program.fee = newProgram['fee']
    program.lateFee = newProgram['lateFee']
    program.billingFrequency = newProgram['billingFrequency']

    program.monthlyBillDay = str(newProgram['monthlyBillDay'])
    program.weeklyBillDay = newProgram['weeklyBillDay']

    program.startDate = datetime.strptime(newProgram['startDate'], DATE_FORMAT).date()

    if newProgram['indefinite']:
        program.indefinite = newProgram['indefinite']
        program.endDate = None
    else:
        program.endDate = datetime.strptime(newProgram['endDate'], DATE_FORMAT).date()

    # program.dueDate = datetime.strptime(newProgram['dueDate'], DATE_FORMAT).date()

    program.put()

    # Deprecated
    # if 'sessions' in data:
    # 	for newSession in data['sessions']:
    # 		session = models.Session(parent=program.key)
    # 		session.sessionName = newSession['sessionName']
    # 		session.repeatOn = newSession['repeatOn']
    # 		session.startTime = datetime.strptime(newSession['startTime'], '%I:%M %p').time()
    # 		session.endTime = datetime.strptime(newSession['endTime'], '%I:%M %p').time()
    # 		session.put()
    return HttpResponse("success")


def list_program_by_child(request):
    status = "failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    provider_id = request.session.get('user_id')
    child_id = long(request.GET.get('child_id'))
    logger.info('provider_id %s, child_id %s' % (provider_id, child_id))
    child_key = Child.generate_key(child_id)
    provider_key = Provider.generate_key(provider_id)
    enrollments = enrollment_util.list_enrollment_by_provider_and_child(provider_key=provider_key, child_key=child_key)
    programs = []
    for enrollment in enrollments:
        programs.append(enrollment.program_key.get())
    response = HttpResponse(json.dumps([JEncoder().encode(program) for program in programs]))
    logger.info("response is %s" % response)
    return response


# Deprecated
# def addSession(request):
# 	"""Adds a new session under the provided program ID for the logged in user"""
# 	email = request.session.get('email')
# 	if not check_session(request):
# 		return HttpResponseRedirect('/login')
#
# 	data = json.loads(request.body)
#
# 	programId = data['programId']
# 	if not programId:
# 		raise Exception('no program id is provided')
#
# 	provider = Provider.get_by_id(email)
# 	program = models.Program.get_by_id(int(programId), parent = provider.key)
#
# 	session = models.Session(parent=program.key)
# 	session.sessionName = data['sessionName']
# 	session.repeatOn = data['repeatOn']
# 	session.startTime = datetime.strptime(data['startTime'], '%I:%M %p').time()
# 	session.endTime = datetime.strptime(data['endTime'], '%I:%M %p').time()
# 	session.put()
# 	return HttpResponse("success")

# Deprecated
# def deleteSession(request):
# 	"""Deletes the session with provided session ID and program ID"""
# 	email = request.session.get('email')
# 	if not check_session(request):
# 		return HttpResponseRedirect('/login')
#
# 	data = json.loads(request.body)
#
# 	programId = data['programId']
# 	sessionId = data['id']
# 	if not programId or not sessionId:
# 		raise Exception('no program id or session id is provided')
#
# 	provider = Provider.get_by_id(email)
# 	program = models.Program.get_by_id(int(programId), parent = provider.key)
#
# 	session = models.Session.get_by_id(int(sessionId), parent = program.key)
# 	session.key.delete()
# 	return HttpResponse("success")

# Deprecated
# def listSessions(request):
# 	"""Handles session listing request. Returns sessions associated with provided program ID"""
# 	email = request.session.get('email')
# 	if not check_session(request):
# 		return HttpResponseRedirect('/login')
# 	if not request.GET.get('id'):
# 		raise Exception('no program id is provided')
#
# 	provider = Provider.get_by_id(email)
# 	# Must specify parent since id is not unique in DataStore
# 	program = models.Program.get_by_id(int(request.GET.get('id')), parent = provider.key)
# 	sessions = models.Session.query(ancestor=program.key)
#
# 	return HttpResponse(json.dumps([JEncoder().encode(session) for session in sessions]))

# Deprecated
# def updateSession(request):
# 	"""Updates the session with provided session ID and program ID"""
# 	email = request.session.get('email')
# 	if not check_session(request):
# 		return HttpResponseRedirect('/login')
#
# 	data = json.loads(request.body)
#
# 	programId = data['programId']
# 	sessionId = data['id']
#
# 	if not programId or not sessionId:
# 		raise Exception('no program id or session id is provided')
# 	provider = Provider.get_by_id(email)
# 	program = models.Program.get_by_id(int(programId), parent = provider.key)
#
# 	session = models.Session.get_by_id(int(sessionId), parent = program.key)
# 	session.sessionName = data['sessionName']
# 	session.repeatOn = data['repeatOn']
# 	session.startTime = datetime.strptime(data['startTime'], '%I:%M %p').time()
# 	session.endTime = datetime.strptime(data['endTime'], '%I:%M %p').time()
# 	session.put()
# 	return HttpResponse("success")
