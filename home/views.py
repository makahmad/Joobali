from common.json_encoder import JEncoder
from common.session import check_session
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import template
from django.http import HttpResponse
from login.models import Provider
from google.appengine.api.app_identity import get_default_version_hostname
from manageprogram.models import Program
import json
import logging
from jose import jwt
from datetime import datetime
import random

def index(request):
	loggedIn = False
	if request.session.get('email'):
		loggedIn = True

	return render_to_response(
		'home/index.html',
		{
			'loggedIn': loggedIn,
			'email': request.session.get('email'),
		    'home_url': get_default_version_hostname()
		 },
		template.RequestContext(request)
	)


def dashboard(request):
	if not check_session(request) or request.session['is_provider'] is False:
		return HttpResponseRedirect('/login')

	#get school name for provider only
	schoolName = None
	provider = Provider.get_by_id(request.session['user_id'])
	if provider is not None:
		schoolName = provider.schoolName

	payload = {
		'name': request.session.get('name'),
		'email': request.session.get('email'),
		'iat': datetime.now(),
		'jti': request.session.get('email')+str(random.getrandbits(64))
	}
	zendesk_token = jwt.encode(payload, '142f1e0db16dae59354211d49d1962cd')

	return render_to_response(
		'home/dashboard.html',
		{
			'loggedIn': True,
			'email': request.session.get('email'),
			'schoolName': schoolName,
			'zendesk_token': zendesk_token,
			'name': request.session.get('name')
		 },
		template.RequestContext(request)
	)

# Deprecated
# def listSessions(program):
# 	"""Returns a list of sessions associated with provided program"""
# 	sessions = Session.query(ancestor=program.key)
#
# 	return HttpResponse(json.dumps([JEncoder().encode(session) for session in sessions]))