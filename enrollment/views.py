from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import template
from wtforms_appengine.ndb import model_form
from . import models
from manageprogram.views import JEncoder
import json
import logging
import re

EnrollmentForm = model_form(models.Enrollment)
logger = logging.getLogger(__name__)


def render_enrollment_home(request):
    """Handles user's request to get enrollment page"""
    logger.info("rendering the enrollment home")

    return render(
        request,
        'enrollment/index.html',
        {},
        template.RequestContext(request)
    )


def add_enrollment(request):
    """Handles HttpRequest about adding a new enrollment"""
    logger.info(request)
    if request.method != 'POST':
        logger.info("get non-post http request")
        return
    logger.info("request.body %s", request.body)
    enrollment_form = EnrollmentForm(data=convert_post_enrollment_data(json.loads(request.body)))
    logger.info("enrollment_form %s" % enrollment_form.data)
    status = ""
    if enrollment_form.validate():
        enrollment = models.Enrollment()
        enrollment_form.populate_obj(enrollment)
        enrollment.status = "initiated"
        enrollment.put()
        status = "success"
    else:
        logger.info("enrollment_form errors: [%s]" % enrollment_form.errors)
        logger.info("enrollment_form not valid")
        status = "failure"
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


def list_enrollment(request):
    """Handles user's request to list all enrollment"""
    # TODO(zilong): add query filter on the current child care provider
    enrollments = models.Enrollment.query()
    return HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollments]))


def convert_post_enrollment_data(enrollment_data):
    """Converts frontend form key into backend form key"""
    new_enrollment_data = dict()
    logger.info(enrollment_data)
    for key in enrollment_data:
        new_enrollment_data[convert_camel_case_to_snake_case(key)] = enrollment_data[key]
    return new_enrollment_data


def convert_camel_case_to_snake_case(name):
    """Converts Camel Case Name to Snake Case Name"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
