from common.session import check_session
from common.json_encoder import JEncoder
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import template
from wtforms_appengine.ndb import model_form
from models import Enrollment
from login.models import Provider
from child import child_util
from google.appengine.ext import ndb
import enrollment_util
import json
import logging
import re

EnrollmentForm = model_form(Enrollment)
logger = logging.getLogger(__name__)


# TODO(zilong): Add session protection for all view methods here


def render_enrollment_home(request):
    """Handles user's request to get enrollment page"""
    if not check_session(request):
        return HttpResponseRedirect('/login')
    logger.info("rendering the enrollment home")

    return render(
        request,
        'enrollment/index.html',
        {},
        template.RequestContext(request)
    )


def add_enrollment(request):
    """Handles HttpRequest about adding a new enrollment"""
    status = "failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    logger.info(request)
    if request.method != 'POST':
        logger.info("get non-post http request")
        return
    logger.info("request.body %s", request.body)
    provider_id = request.session.get("email")
    request_body_dict = json.loads(request.body)
    logger.info(request_body_dict)
    child_key = child_util.get_child_key(request_body_dict['child_id'], request_body_dict['parent_email'])
    program_key = ndb.Key('Provider', provider_id, 'Program', request_body_dict['program_id'])
    child = child_key.get()
    program = program_key.get()
    if child is None:
        logger.info("child does not exist")
    elif program is None:
        logger.info('program does not exist')
    else:
        request_body_dict['start_date']
        enrollment = {
            'provider_key': ndb.Key('Provider', provider_id),
            'child_key' : child_key,
            'program_key' : program_key,
            'status': 'initiated',
            'start_date':request_body_dict['start_date']
        }
        enrollment_util.upsert_enrollment(enrollment)
        status = "success"
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


def add_enrollment_from_child_view(request):
    status = "failure"


def list_enrollment(request):
    """Handles user's request to list all enrollment"""
    enrollments = []
    if not check_session(request):
        return HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollments]))
    provider_id = request.session.get('email')
    enrollments = enrollment_util.list_enrollment_by_provider(provider_id)
    response = HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollments]))
    logger.info("response is %s" % response)
    return response


# TODO(zilong): finish this two methods
def update_enrollment(request):
    enrollment = enrollment_util.upsert(request.enrollment)
    response = HttpResponse(json.dumps(JEncoder().encode(enrollment)))
    return response


def get_enrollment(request):
    status = "Failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    provider_id = request.session.get('email')
    if request.method != 'GET':
        logger.info("get non-post http request")
        # TODO(zilong): return error in this case
        return
    enrollment_id = request.GET.get('enrollmentId', '')
    program_id = request.GET.get('programId', '')
    if len(enrollment_id) == 0:
        logger.info("did not receive an enrollmentId")
        return
    enrollment_id = int(enrollment_id)
    program_id = int(program_id)
    enrollment = enrollment_util.get_enrollment(provider_id, program_id, enrollment_id)
    response = HttpResponse(json.dumps(JEncoder().encode(enrollment)))
    return response


def convert_camel_case_to_snake_case(name):
    """Converts Camel Case Name to Snake Case Name"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
