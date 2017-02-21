import json
import logging

from django.http import HttpResponse, HttpResponseServerError
from django.http import HttpResponseRedirect

from common.json_encoder import JEncoder
from common.session import check_session
from login.models import Provider
from passlib.apps import custom_app_context as pwd_context

logger = logging.getLogger(__name__)


def getProfile(request):
    """Handles get profile request. Returns the profile with provided email"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])
    if provider is not None:
        return HttpResponse(json.dumps([JEncoder().encode(provider)]))

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))


def updateProfile(request):
    """Updates the program with provided program ID"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    profile = json.loads(request.body)

    if not profile['id']:
        raise Exception('no profile id is provided')

    # provider profile update
    provider = Provider.get_by_id(request.session['user_id'])

    if request.session['email'] != profile['email']:
        if request.session['is_provider']:
            query = Provider.query().filter(Provider.email == profile['email'])
            result = query.fetch(1)
            if result:
                return HttpResponseServerError('email already exists')
            request.session['email'] = profile['email']

    if provider is not None:
        provider.schoolName = profile['schoolName']
        provider.firstName = profile['firstName']
        provider.lastName = profile['lastName']
        # todo update transactions tied to this email address
        provider.email = profile['email']
        provider.password = pwd_context.encrypt(profile['password'])
        provider.phone = profile['phone']
        provider.website = profile['website']
        provider.license = profile['license']
        provider.put()

    # return render_to_response(
    # 	'profile/profile_component_tmpl.html',
    # 	{'form': profile},
    # 	template.RequestContext(request)
    # )

    return HttpResponse('success')


def validateEmail(request):
    """Validates user email. Successful if email does not already exist in the system, otherwise failure"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    email = json.loads(request.body)

    provider = Provider.get_by_id(request.session['user_id'])

    if request.session['email'] != email:
        if request.session['is_provider']:
            query = Provider.query().filter(Provider.email == email)
            result = query.fetch(1)
            if result:
                return HttpResponseServerError('failure')

    return HttpResponse('success')