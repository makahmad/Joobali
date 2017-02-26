import json

from common.json_encoder import JEncoder
from common.session import check_session
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import template
from passlib.apps import custom_app_context as pwd_context
from models import Parent


def index(request):
    if not check_session(request) or request.session['is_provider'] is True:
        return HttpResponseRedirect('/login')
    return render_to_response(
        'parent/index.html',
        {
            'loggedIn': True,
            'email': request.session.get('email')
        },
        template.RequestContext(request)
    )


def getProfile(request):
    """Handles get profile request. Returns the profile with provided email"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if request.session['is_provider']:
        return HttpResponseRedirect('/login')

    parent = Parent.get_by_id(request.session['user_id'])
    if parent is not None:
        return HttpResponse(json.dumps([JEncoder().encode(parent)]))

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))


def updateProfile(request):
    """Updates the program with provided program ID"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if request.session['is_provider']:
        return HttpResponseRedirect('/login')

    profile = json.loads(request.body)

    if not profile['id']:
        raise Exception('no profile id is provided')

    # provider profile update
    parent = Parent.get_by_id(request.session['user_id'])

    if request.session['email'] != profile['email']:
        query = Parent.query().filter(Parent.email == profile['email'])
        result = query.fetch(1)
        if result:
            return HttpResponseServerError('email already exists')
        request.session['email'] = profile['email']

    if parent is not None:
        parent.first_name = profile['first_name']
        parent.last_name = profile['last_name']
        # todo for Rongjian update transactions tied to this email address and Unique object
        parent.email = profile['email']
        parent.password = pwd_context.encrypt(profile['password'])
        parent.phone = profile['phone']
        parent.put()

    return HttpResponse('success')


def validateEmail(request):
    """Validates user email. Successful if email does not already exist in the system, otherwise failure"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    email = json.loads(request.body)

    parent = Parent.get_by_id(request.session['user_id'])

    if request.session['email'] != email:
        if not request.session['is_provider']:
            query = Parent.query().filter(Parent.email == email)
            result = query.fetch(1)
            if result:
                return HttpResponseServerError('failure')

    return HttpResponse('success')
