# External Libraries
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
import json
import logging

# Internal Libraries
from common.session import check_session
from common.session import get_provider_id
from common.json_encoder import JEncoder
from child import child_util
from child.models import Child
from parent import parent_util
from login.models import Provider


# Create your views here.

logger = logging.getLogger(__name__)


def list_child(request):
    if not check_session(request):
        return HttpResponseRedirect('/login')
    provider_email = get_provider_id(request)
    provider_key = ndb.Key('Provider', provider_email)
    children = child_util.list_child(provider_key=provider_key)
    return HttpResponse(json.dumps([JEncoder().encode(child) for child in children]), content_type="application/json")


def add_child(request):
    if not check_session(request):
        return HttpResponseRedirect('/login')
    response = dict()
    if request.method != 'POST':
        logger.info('request.method is %s', request.method)
        response['status'] = 'failure'
    else:
        logger.info('request.body is %s', request.body)
        request_content = json.loads(request.body)
        logger.info('request content is %s', request_content)
        provider_key = ndb.Key('Provider', get_provider_id(request))
        parent_input = {'email': request_content['email']}
        parent_entity = parent_util.add_parent_for_child(parent_input)
        child_input = {
            'first_name': request_content['first_name'],
            'last_name': request_content['last_name'],
            'date_of_birth': request_content['date_of_birth'],
            'parent_email': request_content['email']}
        existing_child = child_util.get_existing_child(child_input, parent_entity.key)
        if existing_child is None:
            existing_child = child_util.add_child(child_input, parent_entity.key)
        child_util.add_provider_child_view(child_key=existing_child.key, provider_key=provider_key)
        response['status'] = 'success'
    return HttpResponse(json.dumps(response), content_type="application/json")


def get_child(request):
    if not check_session(request):
        return HttpResponseRedirect('/login')
    response = dict()
    response['status'] = 'failure'
    if request.method == 'GET' or request.method == 'POST':
        if request.method == 'GET':
            child_id = request.get('child_id')
        else:
            request_content = json.loads(request.body)
            child_id = request_content['child_id']
        provider_key = Provider.generate_key(request.session.get('user_id'))
        child_key = Child.generate_key(child_id)
        if child_util.check_child_provider_view(child_key=child_key, provider_key=provider_key):
            return HttpResponse(JEncoder().encode(child_key.get().to_dict()), content_type='application/json')
        else:
            logger.warning("provider %s trying to access %s" % (request.session.get('user_id'), child_id))
    else:
        logger.info('request.method is %s', request.method)
    return HttpResponse(json.dumps(response), content_type="application/json")


def update_child(request):
    pass
