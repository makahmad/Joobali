# External Libraries
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.ext import ndb
import json
import logging

# Internal Libraries
from common import session
from common.json_encoder import JEncoder
from manageprogram.models import Program
from child import child_util
from child.models import Child
from parent import parent_util
from parent.models import Parent
from login.models import Provider
from enrollment import enrollment_util


# Create your views here.

logger = logging.getLogger(__name__)


def list_child(request):
    if not session.check_session(request):
        return HttpResponseRedirect('/login')
    if session.is_provider(request):
        provider_id = session.get_provider_id(request)
        if 'programId' in request.GET:
            program_id = request.GET['programId']
            children = child_util.list_child_by_provider_program(provider_id=provider_id, program_id=program_id)
        else:
            provider_key = Provider.generate_key(provider_id)
            children = child_util.list_child_by_provider(provider_key=provider_key)
    else:
        parent_id = request.session['user_id']
        parent_key = Parent.generate_key(parent_id)
        children = child_util.list_child_by_parent(parent_key=parent_key)
    return HttpResponse(json.dumps([JEncoder().encode(child) for child in children]), content_type="application/json")


def add_child(request):
    if not session.check_session(request) or not session.is_provider(request):
        return HttpResponseRedirect('/login')
    response = dict()
    if request.method != 'POST':
        logger.info('request.method is %s', request.method)
        response['status'] = 'failure'
    else:
        request_content = json.loads(request.body)
        child_first_name = request_content['first_name']
        child_last_name = request_content['last_name']
        date_of_birth = request_content['date_of_birth']
        parent_email = request_content['email']
        program = request_content['program']
        enrollment_start_date = request_content['enrollment_start_date']

        # Setup Parent entity for child
        provider_key = Provider.generate_key(session.get_provider_id(request))
        parent = parent_util.setup_parent_for_child(email=request_content['email'], provider_key=provider_key,
                                                    child_first_name=child_first_name)

        # Setup Child entity
        to_be_added_child = Child.generate_child_entity(child_first_name, child_last_name, date_of_birth, parent_email)
        existing_child = child_util.get_existing_child(to_be_added_child, parent.key)
        if existing_child is not None:
            return HttpResponse(json.dumps(response), content_type="application/json")
        existing_child = child_util.add_child(to_be_added_child, parent.key)
        provider_key = ndb.Key('Provider', session.get_provider_id(request))
        child_util.add_provider_child_view(child_key=existing_child.key, provider_key=provider_key)

        # Setup first enrollment for child
        program_key = Program.generate_key(provider_id=session.get_provider_id(request), program_id=program['id'])
        enrollment_input = {
            'child_key': existing_child.key,
            'provider_key': provider_key,
            'program_key': program_key,
            'status': 'initialized',
            'start_date': enrollment_start_date
        }
        enrollment = enrollment_util.upsert_enrollment(enrollment_input, host=request.get_host())

        if parent.invitation.token is None:
            # The parent already signup
            parent_util.notify_parent_for_enrollment(parent, enrollment)
        else:
            # The parent has not yet signup
            parent_util.invite_parent_for_enrollment(parent, enrollment)
        response['status'] = 'success'
    return HttpResponse(json.dumps(response), content_type="application/json")


def get_child(request):
    if not session.check_session(request):
        return HttpResponseRedirect('/login')
    response = dict()
    response['status'] = 'failure'
    if request.method == 'GET' or request.method == 'POST':
        if request.method == 'GET':
            child_id = request.get('child_id')
        else:
            request_content = json.loads(request.body)
            child_id = request_content['child_id']
        provider_key = Provider.generate_key(session.get_provider_id(request))
        child_key = Child.generate_key(child_id)
        if child_util.check_child_provider_view(child_key=child_key, provider_key=provider_key):
            return HttpResponse(JEncoder().encode(child_key.get().to_dict()), content_type='application/json')
        else:
            logger.warning("provider %s trying to access %s" % (request.session.get('user_id'), child_id))
    else:
        logger.info('request.method is %s', request.method)
    return HttpResponse(json.dumps(response), content_type="application/json")


# TODO(zilong): Implement this
def update_child(request):
    pass
