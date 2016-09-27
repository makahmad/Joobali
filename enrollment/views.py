from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import template
from wtforms_appengine.ndb import model_form
from . import models
from manageprogram.views import JEncoder
import json
import logging

EnrollmentForm = model_form(models.Enrollment)
logger = logging.getLogger(__name__)


def render_enrollment_home(request):
    """handles user's request to the enrollment page"""
    logger.info("rendering the enrollment home")

    return render(
        request,
        'enrollment/index.html',
        {},
        template.RequestContext(request)
    )


def add_enrollment(request):
    logger.info("add enrollment")
    if request.method != 'POST':
        return
    enrollment_form = EnrollmentForm(request.POST)
    if enrollment_form.validate():
        enrollment = models.Enrollment()
        enrollment_form.populate_obj(enrollment)
        enrollment.status = "initiated"
        enrollment.put()
    return HttpResponseRedirect('/enrollment')


def list_enrollment(request):
    """handles user's request to list all enrollment"""
    # TODO(zilong): add query filter on the current child care provider
    enrollments = models.Enrollment.query()
    return HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollments]))
