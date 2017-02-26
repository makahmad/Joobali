from google.appengine.ext import ndb
from models import Enrollment
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def upsert_enrollment(enrollment_input):
    """Upserts an enrollment"""
    enrollment = Enrollment(parent=enrollment_input['provider_key'])
    enrollment.child_key = enrollment_input['child_key']
    enrollment.program_key = enrollment_input['program_key']
    enrollment.status = enrollment_input['status']
    if enrollment.status not in Enrollment.get_possible_status():
        raise RuntimeError('invalid status %s for enrollment' % enrollment.status)
    enrollment.start_date = datetime.strptime(enrollment_input['start_date'], "%m/%d/%Y").date()
    enrollment.put()
    return enrollment


def cancel_enrollment(provider_id, enrollment_id):
    """Cancels an enrollment"""
    enrollment_key = Enrollment.generate_key(provider_id=provider_id, enrollment_id=enrollment_id)
    if enrollment_key.get() is None:
        return None
    enrollment = enrollment_key.get()
    if enrollment.status == 'invited' or enrollment.status == 'initialized' or enrollment.status == 'active':
        enrollment.status = 'inactive'
        enrollment.put()
        return True
    else:
        return False


def reactivate_enrollment(provider_id, enrollment_id):
    """Reactivates an enrollment"""
    enrollment_key = Enrollment.generate_key(provider_id=provider_id, enrollment_id=enrollment_id)
    if enrollment_key.get() is None:
        return None
    enrollment = enrollment_key.get()
    if enrollment.status == 'inactive':
        enrollment.status = 'initialized'
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


def list_enrollment_by_provider_and_child(provider_id, child_key):
    provider_key = ndb.Key('Provider', provider_id)
    enrollment_query = Enrollment.query(Enrollment.child_key==child_key, ancestor=provider_key)
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
        enrollments.append(enrollment.to_dict())
    return enrollments
