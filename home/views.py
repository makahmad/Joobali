from django.shortcuts import render_to_response
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
