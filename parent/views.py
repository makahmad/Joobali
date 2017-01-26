from common.json_encoder import JEncoder
from common.session import check_session
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import template
from django.http import HttpResponse
from login.models import Provider
from manageprogram.models import Program
# Create your views here.

def index(request):
	if not check_session(request):
		return HttpResponseRedirect('/login')
	return render_to_response(
		'parent/index.html',
		{
			'loggedIn': True,
			'email': request.session.get('email')
		 },
		template.RequestContext(request)
	)