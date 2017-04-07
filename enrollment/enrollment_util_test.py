import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from login.models import Provider
from child.models import Child

import enrollment_util
from manageprogram.models import Program


class EnrollmentUtilTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def test_upsert_enrollment(self):
        """
        test_provider = Provider()
        test_provider.lastName = 'Test_LastName'
        test_provider.firstName = 'Test_FirstName'
        test_provider.password = 'Test_Password'
        test_provider.email = 'Test_Email'
        test_provider.schoolName = 'Test_schoolName'

        test_program = Program().put()
        test_enrollment_input = {
            'provider_key': test_provider.key,
            'child_key': test_child.key,
            'program_key': test_program.key,
            'status': 'inactive',
            'start_date': '02/15/2017'
        }
        new_enrollment = enrollment_util.upsert_enrollment(test_enrollment_input)
        self.assertEqual('status', new_enrollment.status)
        """

if __name__ == '__main__':
    unittest.main()
