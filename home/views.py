from common.json_encoder import JEncoder
from common.session import check_session
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import template
from django.http import HttpResponse
from login.models import Provider
from manageprogram.models import Program
from manageprogram.models import Session

import json
import logging

def index(request):
	loggedIn = False
	if request.session.get('email'):
		loggedIn = True

	return render_to_response(
		'home/index.html',
		{
			'loggedIn': loggedIn,
			'email': request.session.get('email')
		 },
		template.RequestContext(request)
	)


def dashboard(request):
	if not check_session(request):
		return HttpResponseRedirect('/login')
	return render_to_response(
		'home/dashboard.html',
		{
			'loggedIn': True,
			'email': request.session.get('email')
		 },
		template.RequestContext(request)
	)


def listPrograms(request):
	"""Handles program listing request. Returns programs and corresponding sessions associated with the logged in user"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')
	provider = Provider.get_by_id(email)
	programs = Program.query(ancestor=provider.key)

	dictPrograms = []
	for program in programs:
		sessions = Session.query(ancestor=program.key)
		dictProgram = program.to_dict()
		dictProgram['id'] = program.key.id()
		dictProgram['sessions'] = [session.to_dict() for session in sessions]
		dictPrograms.append(dictProgram)
	return HttpResponse(json.dumps([JEncoder().encode(dictProgram) for dictProgram in dictPrograms]))

def listSessions(program):
	"""Returns a list of sessions associated with provided program"""
	sessions = Session.query(ancestor=program.key)

	return HttpResponse(json.dumps([JEncoder().encode(session) for session in sessions]))