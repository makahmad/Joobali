import json
import logging

from django.http import HttpResponse, HttpResponseServerError
from django.http import HttpResponseRedirect

from common.json_encoder import JEncoder
from common.session import check_session
from login import unique_util
from login.models import Provider
from passlib.apps import custom_app_context as pwd_context
from google.appengine.ext import ndb
from common.dwolla import update_customer, get_customer, upload_document, list_documents, get_document
from datetime import datetime
from dwollav2.error import ValidationError
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)

DATE_FORMAT = '%m/%d/%Y'

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

def getProviderDoc(request):
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
        return HttpResponse(provider.doc, content_type=provider.docContentType)

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))

def getProfile(request):
    """Handles get profile request. Returns the profile with provided email"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])
    if provider is not None:
        provider.logo = None  # set to none as HTTP response encode breaks for blobs
        provider.doc = None  # set to none as HTTP response encode breaks for blobs
        dict = provider.to_dict()

        dict['id'] = provider.key.id()
        dict['ssn'] = provider.ssn if provider.ssn else None

        dict['zipcode'] = ''
        if provider.zipcode:
            dict['zipcode'] = int(provider.zipcode)
        dict['dateOfBirth'] = provider.dateOfBirth.strftime(DATE_FORMAT) if provider.dateOfBirth else None
        logger.info("Dwolla Status: %s" % dict['dwolla_status'])

        documents = list_documents(provider.customerId)

        for doc in documents['documents']:
            dict['docStatus'] = doc['status']
            pass
        if dict['dwolla_status'] == None or dict['dwolla_status'] == '':
            try:
                dwolla_customer = get_customer(provider.customerId)
                if dwolla_customer:
                    dict['dwolla_status'] = dwolla_customer['status']
            except ValidationError:
                dict['dwolla_status'] = 'Unknown'
        return HttpResponse(json.dumps([JEncoder().encode(dict)]))

    # todo Must specify parent since id is not unique in DataStore
    return HttpResponse(json.dumps([JEncoder().encode(None)]))

def get_dwolla_status(request):
    """Handles get profile request. Returns the profile with provided email"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])
    if provider is not None:
        if provider.dwolla_status is None or provider.dwolla_status == '':
            try:
                dwolla_customer = get_customer(provider.customerId)
                if dwolla_customer:
                    provider.dwolla_status = dwolla_customer['status']
                    provider.put()
            except ValidationError:
                provider.dwolla_status = None
        return HttpResponse(provider.dwolla_status)
    return HttpResponse('Unknown')

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

        unique_util.update_provider(provider.email, profile['email'], provider.key)
        provider.addressLine1 = profile['addressLine1']
        provider.addressLine2 = profile['addressLine2']
        provider.city = profile['city']
        provider.state = profile['state']
        provider.zipcode = str(profile['zipcode'])
        provider.email = profile['email']
        provider.phone = profile['phone']
        provider.website = profile['website']
        provider.license = profile['license']
        #provider.ssn = str(profile['ssn'])

        provider.dateOfBirth = datetime.strptime(profile['dateOfBirth'], DATE_FORMAT) if profile['dateOfBirth'] else None
        provider.tin = profile['tin']

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


def dwolla_verify(request):
    """Updates the provider profile"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if not request.session['is_provider']:
        return HttpResponseRedirect('/login')

    profile = json.loads(request.body)

    # provider profile update
    provider = Provider.get_by_id(request.session['user_id'])

    if request.session['email'] != profile['email']:
        query = Provider.query().filter(Provider.email == profile['email'])
        result = query.fetch(1)
        if result:
            return HttpResponseServerError('email already exists')
        request.session['email'] = profile['email']

    if provider is not None:
        request_body = {
            'firstName': profile['firstName'],
            'lastName': profile['lastName'],
            'email': profile['email'],
            'type': 'personal', # TODO support business type
            'address1': profile['addressLine1'],
            'city': profile['city'],
            'state': profile['state'],
            'postalCode': profile['zipcode'],
            'dateOfBirth': datetime.strptime(profile['dateOfBirth'], DATE_FORMAT).date().strftime('%Y-%m-%d'),
            'ssn': profile['ssn'],
        }
        customer = None
        try:
            customer = update_customer(provider.customerId, request_body)
            logger.info("customer %s" % customer.body)
        except ValidationError as err:  # ValidationError as err
            logger.warning(err)
            return HttpResponse('Account Verification Failed: %s' % err.body['_embedded']['errors'][0]['message'])

        provider.schoolName = profile['schoolName']
        provider.firstName = profile['firstName']
        provider.lastName = profile['lastName']

        unique_util.update_provider(provider.email, profile['email'], provider.key)
        provider.addressLine1 = profile['addressLine1']
        provider.addressLine2 = profile['addressLine2']
        provider.city = profile['city']
        provider.state = profile['state']
        provider.zipcode = str(profile['zipcode'])
        provider.email = profile['email']
        #provider.ssn = str(profile['ssn'])
        provider.dateOfBirth = datetime.strptime(profile['dateOfBirth'], DATE_FORMAT).date()
        if customer and 'status' in customer.body:
            provider.dwolla_status = customer.body['status']
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

def updateDoc(request):
    """Updates the provider's document for dwolla verification"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if not request.session['is_provider']:
        return HttpResponseRedirect('/login')

    provider = Provider.get_by_id(request.session['user_id'])

    if 'file' in request.FILES and request.POST.get('docType') is not None:
        upload_document(provider.customerId, BytesIO(request.FILES['file'].read()), request.POST.get('docType'))
        provider.doc = request.FILES['file'].read()
        provider.docContentType = request.FILES['file'].content_type
        provider.docType = request.POST.get('docType')
        provider.docName = request.FILES['file'].name
    else:
        provider.doc = None
        provider.docContentType = None
        provider.docType = None
        provider.docName = None

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
