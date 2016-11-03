from common.session import check_session
from common.json_encoder import JEncoder
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import template
from wtforms_appengine.ndb import model_form
from google.appengine.ext import ndb
from models import Enrollment
from manageprogram.models import Program
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
    enrollment_form = EnrollmentForm(data=request_body_dict)
    if enrollment_form.validate():
        program_key = ndb.Key('Provider', provider_id, 'Program', request_body_dict['program_id'])
        logger.info("program_key %s" % program_key)
        if program_key.get() is None:
            programs = Program.query()
            for program in programs:
                logger.info("program %s" % program)
            status = "failure"
        else:
            # TODO(zilong): check whether program belongs to the current provider
            enrollment = Enrollment(parent=program_key)
            enrollment_form.populate_obj(enrollment)
            enrollment.status = "initiated"
            enrollment.put()
            status = "success"
    else:
        logger.info("enrollment_form errors: [%s]" % enrollment_form.errors)
        logger.info("enrollment_form not valid")
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


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
