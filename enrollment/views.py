import json
import logging

from datetime import datetime
from django import template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from google.appengine.api.app_identity import get_default_version_hostname
from google.appengine.ext import ndb

import enrollment_util
from child import child_util
from child.models import Child, ProviderChildView
from common.email.enrollment import send_parent_enrollment_notify_email
from common.exception.JoobaliRpcException import JoobaliRpcException
from common.json_encoder import JEncoder
from common.session import check_session
from common.session import get_parent_id
from common.session import get_provider_id
from common.session import is_parent
from common.session import is_provider
from login.models import Provider
from models import Enrollment
from parent.models import Parent
from common import datetime_util

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
    message = ""
    if not check_session(request):
        return
    logger.info(request)
    if request.method != 'POST':
        logger.info("get non-post http request")
        return
    logger.info("request.body %s", request.body)
    provider_id = request.session.get("user_id")
    request_body_dict = json.loads(request.body)
    logger.info(request_body_dict)
    child_key = child_util.get_child_key(request_body_dict['child_id'])
    program_key = ndb.Key('Provider', provider_id, 'Program', request_body_dict['program_id'])
    child = child_key.get()
    program = program_key.get()

    waive_registration = False if 'waive_registration' not in request_body_dict else request_body_dict[
        'waive_registration']

    if child is None:
        logger.info("child does not exist")
    elif program is None:
        logger.info("program_key is %s" % program_key)
        logger.info('program does not exist')
    else:
        request_body_dict['start_date']
        enrollment_input = {
            'provider_key': ndb.Key('Provider', provider_id),
            'child_key': child_key,
            'program_key': program_key,
            'status': 'initialized',
            'start_date': request_body_dict['start_date'],
            'end_date': request_body_dict['end_date'],
            'waive_registration': waive_registration
        }
        logger.info("enrollment is %s", enrollment_input)
        try:
            enrollment = enrollment_util.upsert_enrollment(enrollment_input)
            send_parent_enrollment_notify_email(enrollment=enrollment, host=get_default_version_hostname())
            status = "success"
        except JoobaliRpcException as e:
            status = 'failure'
            message = e.get_client_messasge()
    return HttpResponse(json.dumps({'status': status, 'message': message}), content_type="application/json")


def list_enrollment(request):
    """Handles user's request to list all enrollment"""
    enrollments = []
    if not check_session(request):
        return HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollments]))
    provider_id = request.session.get('email')
    enrollments = enrollment_util.list_enrollment_by_provider(provider_id)
    for enrollment in enrollments:
        enrollment['start_date'] = datetime_util.utc_to_local(enrollment['start_date'])
        enrollment['end_date'] = datetime_util.utc_to_local(enrollment['end_date'])
    response = HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollments]))
    logger.info("response is %s" % response)
    return response


def list_enrollment_by_child(request):
    status = "failure"
    if not check_session(request):
        return HttpResponse(json.dumps({'status': status}), content_type="application/json")
    request_body_dict = json.loads(request.body)
    if is_provider(request):
        # List enrollments for a provider
        provider_key = Provider.generate_key(request.session.get('user_id'))
        child_key = child_util.get_child_key(child_id=request_body_dict['child_id'])
        logger.info('provider_key %s, child_key %s' % (provider_key, child_key))
        enrollments = enrollment_util.list_enrollment_by_provider_and_child(provider_key=provider_key,
                                                                            child_key=child_key)
        enrollment_results = list()
        for enrollment in enrollments:
            enrollment_results.append({
                'enrollment': enrollment,
                'program': enrollment.program_key.get()
            })
        response = HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollment_results]))
        return response
    if is_parent(request):
        # List enrollments for a parent
        child = Child.generate_key(request_body_dict['child_id']).get()
        parent = Parent.generate_key(get_parent_id(request)).get()
        if parent.key != child.parent_key:
            return
        provider_child_view_query = ProviderChildView.query_by_child_id(child.key.id())
        enrollments = list()
        for provider_child_view in provider_child_view_query:
            provider_key = provider_child_view.provider_key
            child_key = provider_child_view.child_key
            enrollments += enrollment_util.list_enrollment_by_provider_and_child(provider_key=provider_key,
                                                                                 child_key=child_key)
        enrollment_results = list()
        for enrollment in enrollments:
            program = enrollment.program_key.get()
            provider = program.key.parent().get()
            enrollment_results.append({
                'enrollment': enrollment,
                'child': enrollment.child_key.get(),
                'program': {
                    'programName': program.programName,
                    'registrationFee': program.registrationFee,
                    'fee': program.fee,
                    'lateFee': program.lateFee,
                    'billingFrequency': program.billingFrequency
                },
                'provider': {
                    'id': provider.key.id(),
                    'schoolName': provider.schoolName
                }
            })
        response = HttpResponse(json.dumps([JEncoder().encode(enrollment) for enrollment in enrollment_results]))
        return response


# TODO(zilong): combine cancel, reactive and accept as one single endpoint
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
    if enrollment_util.cancel_enrollment(provider_id=provider_id, enrollment_id=enrollment_id, host=request.get_host()):
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
    if enrollment_util.reactivate_enrollment(provider_id=provider_id, enrollment_id=enrollment_id,
                                             host=get_default_version_hostname()):
        status = 'success'
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


def accept_enrollment(request):
    status = "failure"
    if not check_session(request):
        return
    logger.info(request)
    if request.method != 'POST':
        logger.info("get non-post http request")
        return
    if not is_parent(request):
        return
    request_body_dict = json.loads(request.body)
    provider_id = request_body_dict['provider_id']
    enrollment_id = request_body_dict['enrollment_id']
    logger.info("provider %s, enrollment_id %s" % (provider_id, enrollment_id))
    if 'date_of_birth' in request_body_dict:
        enrollment = Enrollment.generate_key(provider_id=provider_id, enrollment_id=enrollment_id).get()
        child_key = enrollment.child_key
        child_util.update_child(child_key, {'date_of_birth': request_body_dict['date_of_birth']})
    parent_id = get_parent_id(request)
    if enrollment_util.accept_enrollment(provider_id=provider_id, enrollment_id=enrollment_id, parent_id=parent_id):
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
            program = enrollment.program_key.get()
            enrollment_detail = {
                'enrollment': enrollment,
                'child': child,
                'program': {
                    'programName': program.programName,
                    'registrationFee': program.registrationFee,
                    'fee': program.fee,
                    'lateFee': program.lateFee,
                    'billingFrequency': program.billingFrequency
                }
            }
            enrollments_details.append(enrollment_detail)
        return HttpResponse(json.dumps(JEncoder().encode(enrollments_details)), content_type='application/json')


def update_enrollment(request):
    if request.method != 'POST':
        return HttpResponse(status=400)
    logger.info(request.body)
    if not check_session(request):
        return HttpResponse(status=401)
    provider_id = get_provider_id(request)
    request_body_dict = json.loads(request.body)
    enrollment_key = Enrollment.generate_key(provider_id, request_body_dict['id'])
    enrollment = enrollment_key.get()
    if enrollment is None:
        return HttpResponse("enrollment does not exists", status=400)
    else:
        if 'status' in request_body_dict:
            enrollment.status = request_body_dict['status']
        elif 'start_date' in request_body_dict:
            enrollment.start_date = datetime_util.local_to_utc(datetime.strptime(request_body_dict['start_date'], "%m/%d/%Y"))
        elif 'end_date' in request_body_dict:
            enrollment.end_date = datetime_util.local_to_utc(datetime.strptime(request_body_dict['end_date'], "%m/%d/%Y"))
        enrollment.put()
        return HttpResponse(status=200)

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
    logger.info("request.get_host() %s", request.get_host())
    send_parent_enrollment_notify_email(enrollment=enrollment, host=get_default_version_hostname())
    status = 'success'
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


def setupAutopay(request):
    status = 'failure'
    data = json.loads(request.body)
    pay_days_before = data['payDaysBefore']
    source = data['bankAccountId']

    parent = Parent.get_by_id(request.session['user_id'])

    enrollment = parent.invitation.enrollment_key.get()
    enrollment.autopay_source_id = source
    enrollment.pay_days_before = int(pay_days_before)
    enrollment.put()

    provider_id = enrollment.key.parent().id()
    enrollment_id = enrollment.key.id()
    parent_id = get_parent_id(request)
    if enrollment_util.accept_enrollment(provider_id=provider_id, enrollment_id=enrollment_id, parent_id=parent_id):
        status = 'success'
    return HttpResponse(status)


def list_statuses(request):
    if check_session(request):
        data = list(Enrollment.get_possible_status())
        return JsonResponse(data, encoder=JEncoder, safe=False)
    else:
        return HttpResponse(status=401)
