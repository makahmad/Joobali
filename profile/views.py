import json
import logging

from django.http import HttpResponse, HttpResponseServerError
from django.http import HttpResponseRedirect

from common.json_encoder import JEncoder
from common.session import check_session
from login.models import Provider
from passlib.apps import custom_app_context as pwd_context


logger = logging.getLogger(__name__)

def getProviderLogo(request):
    """Handles get provider logo request. Returns logo if one exists. """
    if request.method != 'GET':
        return
    provider_id = request.GET.get('id', None)
    provider = None
    print provider_id
    if provider_id:
        provider = Provider.get_by_id(int(provider_id))

    if provider is None:
        if not check_session(request):
            return HttpResponseRedirect('/login')
        provider = Provider.get_by_id(request.session['user_id'])

    if provider is not None:
        return HttpResponse(provider.logo, content_type="image/jpeg")

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))


def getProfile(request):
    """Handles get profile request. Returns the profile with provided email"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])
    if provider is not None:
        provider.logo = None  # set to none as HTTP response encode breaks for blobs
        return HttpResponse(json.dumps([JEncoder().encode(provider)]))

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))


def updateProfile(request):
    """Updates the provider profile"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if not request.session['is_provider']:
        return HttpResponseRedirect('/login')

    profile = json.loads(request.body)
    if not profile['id']:
        raise Exception('no profile id is provided')

    # provider profile update
    provider = Provider.get_by_id(request.session['user_id'])

    if request.session['email'] != profile['email']:
        query = Provider.query().filter(Provider.email == profile['email'])
        result = query.fetch(1)
        if result:
            return HttpResponseServerError('email already exists')
        request.session['email'] = profile['email']

    if provider is not None:
        if 'currentPassword' in profile and 'newPassword' in profile:
            if pwd_context.verify(profile['currentPassword'], provider.password):
                provider.password = pwd_context.encrypt(profile['newPassword'])
            else:
                return HttpResponseServerError('current password is incorrect')

        provider.schoolName = profile['schoolName']
        provider.firstName = profile['firstName']
        provider.lastName = profile['lastName']
        # todo for Rongjian update transactions tied to this email address and Unique object
        provider.email = profile['email']
        provider.phone = profile['phone']
        provider.website = profile['website']
        provider.license = profile['license']

        if 'currentPassword' in profile and 'newPassword' in profile and pwd_context.verify(profile['currentPassword'],
                                                                                            provider.password):
            provider.password = pwd_context.encrypt(profile['newPassword'])

        provider.put()

    # return render_to_response(
    # 	'profile/profile_component_tmpl.html',
    # 	{'form': profile},
    # 	template.RequestContext(request)
    # )

    return HttpResponse('success')


def updateLogo(request):
    """Updates the provider's logo"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if not request.session['is_provider']:
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])
    provider.logo = request.body

    if request.body:
        provider.showLogo = True
    else:
        provider.showLogo = False

    provider.put()

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
