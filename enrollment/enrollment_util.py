import logging
from datetime import datetime

from google.appengine.ext import ndb

from common.email.enrollment import send_unenroll_email, send_parent_enrollment_notify_email
from common.exception.JoobaliRpcException import JoobaliRpcException
from login.models import Provider
from manageprogram.models import Program
from models import Enrollment
from invoice import invoice_util
from parent.models import Parent
from datetime import datetime, date
from manageprogram import program_util
from common import datetime_util

logger = logging.getLogger(__name__)


def validate_enrollment_date(program, start_date, end_date):
    # Check start date
    start_date_delta = start_date - program.startDate
    if start_date_delta.days < 0:
        raise JoobaliRpcException(client_viewable_message="The enrollment start date is earlier than the program start date.")
    if program.endDate is not None:
        end_date_delta = program.endDate - end_date
        if end_date_delta.days < 0:
            raise JoobaliRpcException(client_viewable_message="The enrollment end date is set after this program ends.")


def upsert_enrollment(enrollment_input):
    """Upserts an enrollment"""
    provider_key = enrollment_input['provider_key']
    child_key = enrollment_input['child_key']
    program_key = enrollment_input['program_key']
    existing_enrollments = list_enrollment_by_provider_and_child_and_program(provider_key, child_key, program_key)
    if len(existing_enrollments) > 0:
        raise JoobaliRpcException(
            error_message="Existing enrollment between this child_key %s and program_key %s" % (child_key, program_key),
            client_viewable_message="There is already an similar existing enrollment")
    enrollment = Enrollment(parent=provider_key)
    enrollment.child_key = child_key
    enrollment.program_key = program_key
    enrollment.status = enrollment_input['status']
    enrollment.waive_registration = enrollment_input['waive_registration']
    if enrollment.status not in Enrollment.get_possible_status():
        raise RuntimeError('invalid status %s for enrollment' % enrollment.status)
    enrollment.start_date = datetime_util.local_to_utc(datetime.strptime(enrollment_input['start_date'], "%m/%d/%Y"))
    enrollment.end_date = datetime_util.local_to_utc(datetime.strptime(enrollment_input['end_date'], "%m/%d/%Y")) if enrollment_input[
        'end_date'] else None

    program = program_key.get()
    if enrollment.end_date is None and program.endDate is not None:
        enrollment.end_date = program.endDate
    # Validate enrollment start date and end date
    validate_enrollment_date(program, enrollment.start_date, enrollment.end_date)

    enrollment.put()

    # Create registration invoice, and payment if already paid.
    invoice = None
    if not enrollment.waive_registration and program.registrationFee > 0:
        provider = provider_key.get()
        child = child_key.get()
        due_date = datetime.now()  # Registration due right at when it's created.
        invoice = invoice_util.create_invoice(provider, child, due_date, None, program.registrationFee,
                                              False)
        invoice_util.create_invoice_line_item(enrollment.key, invoice, program, None, None, "Registration Fee",
                                              program.registrationFee)

    return enrollment, invoice


def cancel_enrollment(provider_id, enrollment_id, host):
    """Cancels an enrollment"""
    enrollment_key = Enrollment.generate_key(provider_id=provider_id, enrollment_id=enrollment_id)
    if enrollment_key.get() is None:
        return None
    enrollment = enrollment_key.get()
    if enrollment.status == 'invited' or enrollment.status == 'initialized' or enrollment.status == 'active':
        enrollment.status = 'inactive'
        enrollment.put()
        send_unenroll_email(enrollment, host)
        return True
    else:
        return False


def reactivate_enrollment(provider_id, enrollment_id, host):
    """Reactivates an enrollment"""
    enrollment_key = Enrollment.generate_key(provider_id=provider_id, enrollment_id=enrollment_id)
    if enrollment_key.get() is None:
        return None
    enrollment = enrollment_key.get()
    if enrollment.status == 'inactive':
        enrollment.status = 'initialized'
        enrollment.put()
        send_parent_enrollment_notify_email(enrollment, host)
        return True
    else:
        return False


def accept_enrollment(provider_id, enrollment_id, parent_id):
    enrollment_key = Enrollment.generate_key(provider_id=int(provider_id), enrollment_id=int(enrollment_id))
    if enrollment_key.get() is None:
        logger.warning('invalid provider_id %s and enrollment_id %s pair' % (provider_id, enrollment_id))
        return None
    enrollment = enrollment_key.get()
    if enrollment.child_key.get().parent_key != Parent.generate_key(parent_id):
        return False
    if enrollment.status == 'invited' or enrollment.status == 'initialized':
        enrollment.status = 'active'
        enrollment.put()
        # DON'T CREATE INVOICE AT ENROLLMENT ACCEPTANCE ANYMORE, CREATE AT ENROLLMENT CREATION...
        # program = enrollment.program_key.get()
        # if not enrollment.waive_registration and program.registrationFee > 0:
        #     provider = enrollment.program_key.parent().get()
        #     child = enrollment.child_key.get()
        #     due_date = datetime.now() # Registration due right at when it's created.
        #     invoice = invoice_util.create_invoice(provider, child, due_date, None, program.registrationFee,
        #                                           False)
        #     invoice_util.create_invoice_line_item(enrollment_key, invoice, program, None, None, "Registration Fee",
        #                                           program.registrationFee)
        return True
    else:
        return False


def get_enrollment(provider_id, enrollment_id):
    """Reads an enrollment given the enrollment id"""
    logger.info("enrollment_id is %d, provider_id %s" % (enrollment_id, provider_id))
    enrollment_key = Enrollment.generate_key(provider_id, enrollment_id)
    enrollment = enrollment_key.get()
    logger.info(enrollment)
    return enrollment


def list_enrollment_by_provider_and_child(provider_key, child_key):
    enrollment_query = Enrollment.query(Enrollment.child_key == child_key,
                                        ancestor=provider_key).order(-Enrollment.start_date)
    enrollments = list()
    for enrollment in enrollment_query:
        enrollments.append(enrollment)
    return enrollments


def list_enrollment_by_provider_and_child_and_program(provider_key, child_key, program_key):
    enrollment_query = Enrollment.query(Enrollment.child_key == child_key, Enrollment.program_key == program_key,
                                        ancestor=provider_key).order(-Enrollment.start_date)

    if enrollment_query is None:
        logger.info("enrollment_query is none")
    enrollments = list()
    for enrollment in enrollment_query:
        enrollments.append(enrollment)
    return enrollments


def list_enrollment_by_provider(provider_id):
    """List all enrollment given a provider id"""
    provider_key = ndb.Key('Provider', provider_id)
    enrollment_query = Enrollment.query(ancestor=provider_key)
    enrollments = []
    for enrollment in enrollment_query:
        enrollment_dict = enrollment.to_dict()
        enrollment_dict['enrollment_id'] = enrollment.key.id()
        enrollments.append(enrollment_dict)
    return enrollments


def list_enrollment_object_by_provider(provider_id):
    """List all enrollment ndb object given a provider id"""
    provider_key = ndb.Key('Provider', provider_id)
    enrollment_query = Enrollment.query(ancestor=provider_key)
    enrollments = []
    for enrollment in enrollment_query:
        enrollments.append(enrollment)
    return enrollments


def list_enrollment_by_provider_program(provider_id, program_id):
    program = Program.generate_key(provider_id, program_id).get()
    if program is None:
        return []
    provider_key = Provider.generate_key(provider_id)
    enrollment_query = Enrollment.query(Enrollment.program_key == program.key, ancestor=provider_key)
    enrollments = list()
    for enrollment in enrollment_query:
        enrollments.append(enrollment)
    return enrollments


def list_active_enrollment_by_provider_program(provider_id, program_id):
    program = Program.generate_key(provider_id, program_id).get()
    if program is None:
        return []
    provider_key = Provider.generate_key(provider_id)
    enrollment_query = Enrollment.query(Enrollment.program_key == program.key, Enrollment.status == 'active', ancestor=provider_key)
    enrollments = list()
    for enrollment in enrollment_query:
        enrollments.append(enrollment)
    return enrollments


def setup_autopay_enrollment(pay_days_before, autopay_source_id, enrollment):
    status = 'Failure'
    enrollment.autopay_source_id = autopay_source_id
    enrollment.pay_days_before = int(pay_days_before)
    enrollment.put()

    parent_key = enrollment.child_key.get().parent_key

    provider_id = enrollment.key.parent().id()
    enrollment_id = enrollment.key.id()
    parent_id = parent_key.id()
    if accept_enrollment(provider_id=provider_id, enrollment_id=enrollment_id, parent_id=parent_id):
        status = 'success'
    return status
