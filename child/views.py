# External Libraries
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from common.request import get_host_from_request
from google.appengine.ext import ndb
import json
import logging

# Internal Libraries
from common import session
from common.exception.JoobaliRpcException import JoobaliRpcException
from common.json_encoder import JEncoder
from common.email.enrollment import send_parent_enrollment_notify_email
from manageprogram.models import Program
from child import child_util
from child.models import Child
from parent import parent_util
from parent.models import Parent
from login.models import Provider
from enrollment import enrollment_util
from payments import payments_util
from datetime import datetime
from common import datetime_util
from invoice import invoice_util

# Create your views here.

DATE_FORMAT = '%m/%d/%Y'
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
    try:
        if request.method != 'POST':
            logger.info('request.method is %s', request.method)
            raise JoobaliRpcException(client_viewable_message="only post method is allowed")
        else:
            request_content = json.loads(request.body)
            child_first_name = request_content['child_first_name']
            child_last_name = request_content['child_last_name']
            date_of_birth = request_content['child_date_of_birth']
            parent_email = request_content['child_parent_email'].lower()
            program = request_content['program']
            billing_start_date = request_content['start_date']
            billing_end_date = request_content['end_date']

            waive_registration = False if 'waive_registration' not in request_content else request_content[
                'waive_registration']

            registration_fee_paid = False if 'registration_fee_paid' not in request_content else request_content[
                'registration_fee_paid']

            overriding_billing_fee = None if 'fee' not in request_content else request_content['fee']

            # Validate enrollment start date and end date
            program_key = Program.generate_key(provider_id=session.get_provider_id(request), program_id=program['id'])
            start_date = datetime_util.local_to_utc(
                datetime.strptime(billing_start_date, "%m/%d/%Y"))
            end_date = datetime_util.local_to_utc(
                datetime.strptime(billing_end_date, "%m/%d/%Y")) if billing_end_date else None
            program_object = program_key.get()
            if end_date is None and program_object.endDate is not None:
                end_date = program_object.endDate
            enrollment_util.validate_enrollment_date(program_object, start_date, end_date)

            # Setup Parent entity for child
            provider_key = Provider.generate_key(session.get_provider_id(request))
            (parent, verification_token) = parent_util.setup_parent_for_child(email=parent_email,
                                                                              provider_key=provider_key,
                                                                              child_first_name=child_first_name)

            # Setup Child entity
            to_be_added_child = Child.generate_child_entity(child_first_name, child_last_name, date_of_birth, parent_email)
            existing_child = child_util.get_existing_child(to_be_added_child, parent.key)
            if existing_child is not None:
                logger.warning("Child already existed: %s", existing_child)
                return HttpResponse("This child was already registered in the system.")

            logger.info("Adding new child: %s", to_be_added_child)
            new_child = child_util.add_child(to_be_added_child, parent.key)
            provider_key = ndb.Key('Provider', session.get_provider_id(request))
            child_util.add_provider_child_view(child_key=new_child.key, provider_key=provider_key)

            # Setup first enrollment for child
            enrollment_input = {
                'child_key': new_child.key,
                'provider_key': provider_key,
                'program_key': program_key,
                'status': 'initialized',
                'start_date': billing_start_date,
                'end_date': billing_end_date,
                'waive_registration': waive_registration,
                'billing_fee': overriding_billing_fee
            }

            logger.info("Adding new enrollment: %s", enrollment_input)
            enrollment, invoice = enrollment_util.upsert_enrollment(enrollment_input)


            if registration_fee_paid:
                payer = request_content['payer'] if 'payer' in request_content else ''
                payment_date = datetime_util.local_to_utc(datetime.strptime(request_content['payment_date'], DATE_FORMAT))
                payment_type = request_content['payment_type'] if 'payment_type' in request_content else ''
                note = request_content['note'] if 'note' in request_content else ''
                payments_util.add_payment_maybe_for_invoice(provider_key.get(), new_child, invoice.amount,
                                                            payer, payment_date, payment_type, note, invoice)

            if parent.status is 'active':
                # The parent already signup
                send_parent_enrollment_notify_email(enrollment, host=get_host_from_request(request.get_host()))
            else:
                # The parent has not yet signup
                parent.invitation.enrollment_key = enrollment.key
                parent.invitation.child_first_name = child_first_name
                parent.invitation.provider_key = provider_key
                parent.put()
                send_parent_enrollment_notify_email(enrollment, host=get_host_from_request(request.get_host()),
                                                    verification_token=verification_token)
            response['status'] = 'success'
    except JoobaliRpcException as e:
        logger.error(e.get_client_messasge())
        return HttpResponse(status=e.get_http_error_code(), content=e.get_client_messasge())

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


def update_child(request):
    if not session.check_session(request):
        return HttpResponseRedirect('/login')

    new_child = json.loads(request.body)
    child_key = Child.generate_key(new_child['id'])
    child_util.update_child(child_key, {'first_name': new_child['first_name'],
                                        'last_name': new_child['last_name'],
                                        'date_of_birth': new_child['date_of_birth']})

    return HttpResponse("success")


def remove_child(request):
    if not session.check_session(request):
        return HttpResponseRedirect('/login')

    new_child = json.loads(request.body)
    child_key = Child.generate_key(new_child['id'])

    child = child_key.get()
    parent = child.parent_key.get()
    if parent.status.status == 'active':
        logger.warning("Parent active. Child not removeable: %s", new_child['id'])
        return HttpResponse(
            "The child of this parent has already signed up. Please contact us to remove this child.")

    if session.is_provider(request):
        provider_id = session.get_provider_id(request)
        provider_key = Provider.generate_key(provider_id)
        can_remove = True
        for enrollment in enrollment_util.list_enrollment_by_provider_and_child(provider_key, child_key):
            if enrollment.is_active():
                can_remove = False
        if can_remove:
            # can_remove_parent = True
            # for other_child in child_util.list_child_by_parent(parent.key):
            #     if other_child != child and child_util.get_provider_child_view(child_key=other_child.key, provider_key=provider_key):
            #         can_remove_parent = False

            invited_enrollment_key = None
            if parent.invitation:
                invited_enrollment_key = parent.invitation.enrollment_key
            for enrollment in enrollment_util.list_enrollment_by_provider_and_child(provider_key, child_key):
                for invoice in invoice_util.get_enrollment_invoices(enrollment):
                    invoice_util.force_delete_invoice(invoice) # delete all related invoices and payments (mostly the registration fee). It's safe because the parent haven't signed up.
                if invited_enrollment_key == enrollment.key:
                    parent.invitation = None # Delete the invitation if we remove the child.
                    parent.put()
                enrollment_util.cancel_enrollment(provider_id, enrollment.key.id(), request.get_host())
            children_views = child_util.get_provider_child_view(child_key=child_key, provider_key=provider_key)

            for view in children_views:
                view.key.delete()

        else:
            logger.warning("Active enrollment. Child not removeable: %s", new_child['id'])
            return HttpResponse("This child is actively enrolled. Please unenroll and try again.")


    return HttpResponse("success")