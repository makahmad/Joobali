from django.shortcuts import render
from django import template

def index(request):
    return render(
        request,
        'enrollment/index.html',
        {},
        template.RequestContext(request)
    )
