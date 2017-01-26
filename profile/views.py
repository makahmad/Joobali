import json
import logging

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from common.json_encoder import JEncoder
from common.session import check_session
from login.models import Provider

logger = logging.getLogger(__name__)


def getProfile(request):
	"""Handles get profile request. Returns the profile with provided email"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')

	provider = Provider.get_by_id(email)
	# Must specify parent since id is not unique in DataStore
	return HttpResponse(json.dumps([JEncoder().encode(provider)]))


def updateProfile(request):
	"""Updates the program with provided program ID"""
	email = request.session.get('email')
	if not check_session(request):
		return HttpResponseRedirect('/login')

	profile = json.loads(request.body)

	if not profile['id']:
		raise Exception('no profile id is provided')

	provider = Provider.get_by_id(email)
	provider.schoolName = profile['schoolName']

	provider.put()

	return HttpResponse('success')