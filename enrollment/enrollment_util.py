from google.appengine.ext import ndb
from models import Enrollment
from datetime import datetime
from common import key_util
import logging

logger = logging.getLogger(__name__)


def upsert_enrollment(enrollment_input):
    """Upserts an enrollment"""
    enrollment = Enrollment(parent=enrollment_input['provider_key'])
    enrollment.child_key = enrollment_input['child_key']
    enrollment.program_key = enrollment_input['program_key']
    enrollment.status = enrollment_input['status']
    enrollment.start_date = datetime.strptime(enrollment_input['start_date'], "%m/%d/%Y").date()
    enrollment.put()
    return enrollment


def delete_enrollment(enrollment):
    """Deletes an enrollment"""
    enrollment_id = enrollment.id
    delete_enrollment_by_id(enrollment_id)
    pass


def delete_enrollment_by_id(enrollment_id):
    """Deletes an enrollment given the enrollment id"""
    pass


def get_enrollment(provider_id, program_id, enrollment_id):
    """Reads an enrollment given the enrollment id"""
    logger.info("enrollment_id is %d, program_id is %d, provider_id %s" % (enrollment_id, program_id, provider_id))
    enrollment_key = get_enrollment_key(provider_id, program_id, enrollment_id)
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
        logger.info("enrollment: %s" % enrollment)
        enrollment_dict = dict()
        enrollment_dict['program_id'] = key_util.get_id_by_kind(enrollment.program_key, 'Program')
        enrollment_dict['status'] = enrollment.status
        enrollment_dict['start_date'] = enrollment.start_date
        enrollments.append(enrollment_dict)
    return enrollments


def list_enrollment_by_provider(provider_id):
    """List all enrollment given a provider id"""
    provider_key = ndb.Key('Provider', provider_id)
    enrollment_query = Enrollment.query(ancestor=provider_key)
    enrollments = []
    for enrollment in enrollment_query:
        program_id = key_util.get_id_by_kind(enrollment.program_key, 'Program')
        enrollment_id = key_util.get_id_by_kind(enrollment.key, 'Enrollment')
        enrollment_dict = enrollment.to_dict();
        enrollment_dict["program_id"] = program_id
        enrollment_dict["enrollment_id"] = enrollment_id
        enrollments.append(enrollment_dict)
    return enrollments

def convert_enrollment_to_dict(enrollment):
    enrollment_dict = dict()
    enrollment_dict['program_id'] = enrollment.key['Program']
    enrollment_dict['provider_id'] = enrollment.key['Provider']
    enrollment_dict += enrollment.to_dict()
    return enrollment_dict


def get_enrollment_key(provider_id, program_id, enrollment_id):
    return ndb.Key("Provider", provider_id, "Program", program_id, "Enrollment", enrollment_id)
