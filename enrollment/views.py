from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import template
from google.appengine.ext import ndb
from common.email.invoice import send_parent_enrollment_notify_email
from common.session import check_session
from common.session import is_provider
from common.session import is_parent
from common.session import get_provider_id
from common.session import get_parent_id
from common.json_encoder import JEncoder
from models import Enrollment
from child import child_util
import enrollment_util
import json
import logging

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
    provider_id = request.session.get("user_id")
    request_body_dict = json.loads(request.body)
    logger.info(request_body_dict)
    parent_email = request_body_dict['parent_email']
    child_key = child_util.get_child_key(request_body_dict['child_id'])
    program_key = ndb.Key('Provider', provider_id, 'Program', request_body_dict['program_id'])
    child = child_key.get()
    program = program_key.get()
    if child is None:
        logger.info("child does not exist")
    elif program is None:
        logger.info("program_key is %s" % program_key)
        logger.info('program does not exist')
    else:
        request_body_dict['start_date']
        enrollment = {
            'provider_key': ndb.Key('Provider', provider_id),
            'child_key': child_key,
            'program_key': program_key,
            'status': 'initialized',
            'start_date': request_body_dict['start_date']
        }
        enrollment_util.upsert_enrollment(enrollment)
        status = "success"
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


def list_enrollment_by_child(request):
    status = "failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    provider_id = request.session.get('user_id')
    request_body_dict = json.loads(request.body)
    logger.info('provider_id %s, child_id %s' % (provider_id, request_body_dict['child_id']))
    child_key = child_util.get_child_key(child_id=request_body_dict['child_id'])
    enrollments = enrollment_util.list_enrollment_by_provider_and_child(provider_id=provider_id, child_key=child_key)
    response = HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollments]))
    logger.info("response is %s" % response)
    return response


def cancel_enrollment(request):
    status = "failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    logger.info(request)
    if request.method != 'POST':
        logger.info("get non-post http request")
        return
    request_body_dict = json.loads(request.body)
    provider_id = request.session.get("user_id")
    enrollment_id = request_body_dict['enrollment_id']
    if enrollment_util.cancel_enrollment(provider_id=provider_id, enrollment_id=enrollment_id):
        status = 'success'
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


def reactivate_enrollment(request):
    status = "failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    logger.info(request)
    if request.method != 'POST':
        logger.info("get non-post http request")
        return
    request_body_dict = json.loads(request.body)
    provider_id = request.session.get("user_id")
    enrollment_id = request_body_dict['enrollment_id']
    if enrollment_util.reactivate_enrollment(provider_id=provider_id, enrollment_id=enrollment_id):
        status = 'success'
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


def get_enrollment(request):
    """
    :param request: the HTTP Request
    :return: a HttpResponse containing either enrollments' basic info, or a list of enrollment details including the
    child info, program info and basic enrollment info.
    The requester's identity will be used to filter results, which can prevent potential privacy issue.
    For provider, only enrollments belonging to the same provider will be returned.
    For Parent, only enrollments concerning his/her child will be returned.
    """
    if not check_session(request):
        return
    if request.method == 'GET':
        provider_id = request.session.get('email')
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
    if request.method == 'POST':
        logger.info('Get a POST request')
        request_body_dict = json.loads(request.body)
        enrollments_details = list()
        filtering_provider_id = None
        filtering_parent_id = None
        if is_provider(request):
            filtering_provider_id = get_provider_id(request)
        if is_parent(request):
            filtering_parent_id = get_parent_id(request)
        for enrollment in request_body_dict['enrollments']:
            provider_id = int(enrollment['provider_id'])
            enrollment_id = int(enrollment['id'])
            enrollment = Enrollment.generate_key(provider_id, enrollment_id).get()
            logger.info('getting enrollment %s' % enrollment)
            if filtering_provider_id is not None:
                if filtering_provider_id != provider_id:
                    logger.warning('provider_id %s try to access {provider_id: %s, enrollment_id: %s}' % (
                        filtering_provider_id, provider_id, enrollment_id))
                    continue
            child = enrollment.child_key.get()
            if filtering_parent_id is not None:
                if filtering_parent_id != child.parent_key.id():
                    logger.warning('parent_id %s try to access {provider_id: %s, enrollment_id: %s} for child %s' % (
                        filtering_parent_id, provider_id, enrollment_id, child.key.id()))
                    continue
            enrollment_detail = {
                'enrollment': enrollment,
                'child': child,
                'program': enrollment.program_key.get()
            }
            enrollments_details.append(enrollment_detail)
        return HttpResponse(json.dumps(JEncoder().encode(enrollments_details)), content_type='application/json')


def resent_enrollment_invitation(request):
    status = "Failure"
    if not check_session(request) or not is_provider(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    if request.method != 'POST':
        logger.info("get non-post http request")
        return
    request_body_dict = json.loads(request.body)
    enrollment_id = request_body_dict['id']
    provider_id = get_provider_id(request)
    enrollment = Enrollment.get(provider_id=provider_id, enrollment_id=enrollment_id)
    if not enrollment.can_resend_invitation():
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    send_parent_enrollment_notify_email(enrollment=enrollment, host="localhost:8080")
    status = 'success'
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


def setupAutopay(request):
    data = json.loads(request.body)
    pay_days_before = data['payDaysBefore']
    source = data['bankAccountId']

    #enrollment = Enrollment.get_by_id()

    enrollment = Enrollment.get_by_id(4563797888991232, parent=ndb.Key('Provider', 12))
    enrollment.autopay_source_id = source
    enrollment.pay_days_before = int(pay_days_before)
    enrollment.put()

    return HttpResponse("success")
