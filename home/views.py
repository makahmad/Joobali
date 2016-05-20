from django.shortcuts import render_to_response
from django import template
from django.http import HttpResponse


def index(request):
	return render_to_response(
		'home/index.html',
		{},
		template.RequestContext(request)
	)
