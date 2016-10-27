from google.appengine.ext import ndb
from models import Enrollment
import logging

logger = logging.getLogger(__name__)

# TODO(zilong): Implement this class
class EnrollmentHelper:
    """Helper class for managing Enrollment information"""

    def __init__(self):
        pass

    def upsert(enrollment):
        """Upserts an enrollment"""
        pass

    def delete(self, enrollment):
        """Deletes an enrollment"""
        enrollment_id = enrollment.id
        self.delete(enrollment_id)
        pass

    def delete(self, enrollment_id):
        """Deletes an enrollment given the enrollment id"""
        pass

    def get(self, provider_id, program_id, enrollment_id):
        """Reads an enrollment given the enrollment id"""
        logger.info("enrollment_id is %d, program_id is %d, provider_id %s" % (enrollment_id, program_id, provider_id))
        enrollment_key = ndb.Key("Provider", provider_id, "Program", program_id, "Enrollment", enrollment_id)
        enrollment = enrollment_key.get()
        logger.info(enrollment)
        return enrollment

    def list_enrollment_by_provider(self, provider_id):
        """List all enrollment given a provider id"""
        provider_key = ndb.Key('Provider', provider_id)
        enrollment_query = Enrollment.query(ancestor=provider_key)
        enrollments = []
        for enrollment in enrollment_query:
            enrollments.append(enrollment)
        return enrollments
