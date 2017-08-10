from common.json_encoder import JEncoder
from common.session import check_session
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django import template
from django.http import HttpResponse
from login.models import Provider,Parent
from manageprogram.models import Program
import json
import logging
from jose import jwt
from datetime import datetime
import random


def index(request):

    return render_to_response(
        'home/index.html',
        {
            'loggedIn': check_session(request),
            'email': request.session.get('email'),
            'home_url': 'https://www.joobali.com'
        },
        template.RequestContext(request)
    )


def dashboard(request):
    if not check_session(request) or request.session['is_provider'] is False:
        return HttpResponseRedirect('/login')

    # get school name for provider only
    schoolName = None
    provider = Provider.get_by_id(request.session['user_id'])
    if provider is not None:
        schoolName = provider.schoolName

    payload = {
        'name': request.session.get('name'),
        'email': request.session.get('email'),
        'iat': datetime.now(),
        'jti': request.session.get('email') + str(random.getrandbits(64))
    }
    zendesk_token = jwt.encode(payload, '06d401e8e50ac108d2da325caa12854c')

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

def admin(request):
    if not check_session(request) or request.session['is_admin'] is False:
        return HttpResponseRedirect('/login')

    if request.method == 'POST':
        email = request.POST.get('email')

        query = Provider.query().filter(Provider.email == email)
        provider = query.get()

        redirect = ''
        if request.POST.get('url') and '#!' in request.POST.get('url'):
            redirect = '/#!' + request.POST.get('url').split('#!')[1]

        if provider is None:
            query = Parent.query().filter(Parent.email == email)
            parent = query.get()
            if parent is None:
                return render_to_response(
                    'home/admin.html',
                    {
                        'error': 'User does not exist'
                    },
                    template.RequestContext(request)
                )
            else:
                request.session['email'] = parent.email
                request.session['name'] = parent.first_name + ' ' + parent.last_name
                request.session['user_id'] = parent.key.id()
                request.session['is_provider'] = False
                request.session['dwolla_customer_url'] = parent.customerId
                return HttpResponseRedirect("/parent" + redirect)

        else:
            request.session['email'] = provider.email
            request.session['name'] = provider.firstName + ' ' + provider.lastName
            request.session['user_id'] = provider.key.id()
            request.session['is_provider'] = True
            request.session['dwolla_customer_url'] = provider.customerId
            return HttpResponseRedirect("/home/dashboard" + redirect)

    return render_to_response(
        'home/admin.html',
        template.RequestContext(request)
    )


    # Deprecated
    # def listSessions(program):
    # 	"""Returns a list of sessions associated with provided program"""
    # 	sessions = Session.query(ancestor=program.key)
    #
    # 	return HttpResponse(json.dumps([JEncoder().encode(session) for session in sessions]))
