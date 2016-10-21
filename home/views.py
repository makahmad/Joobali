from common.session import check_session
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import template
from django.http import HttpResponse



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