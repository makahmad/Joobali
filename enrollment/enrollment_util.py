import logging
from datetime import datetime

from google.appengine.ext import ndb

from common.email.enrollment import send_unenroll_email, send_parent_enrollment_notify_email
from common.exception import JoobaliRpcException
from login.models import Provider
from manageprogram.models import Program
from models import Enrollment
from parent.models import Parent

logger = logging.getLogger(__name__)


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
    enrollment.start_date = datetime.strptime(enrollment_input['start_date'], "%m/%d/%Y").date()
    enrollment.put()
    return enrollment


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
    enrollment_query = Enrollment.query(Enrollment.child_key == child_key, ancestor=provider_key)
    enrollments = list()
    for enrollment in enrollment_query:
        enrollments.append(enrollment)
    return enrollments


def list_enrollment_by_provider_and_child_and_program(provider_key, child_key, program_key):
    enrollment_query = Enrollment.query(Enrollment.child_key == child_key, Enrollment.program_key == program_key,
                                        ancestor=provider_key)

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
