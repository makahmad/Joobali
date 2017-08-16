import unittest

from datetime import datetime
from google.appengine.ext import testbed, ndb

from child.models import Child
from common.exception.JoobaliRpcException import JoobaliRpcException
from enrollment import enrollment_util
from login.models import Provider
from manageprogram.models import Program
from manageprogram.views import DATE_FORMAT
from parent.models import Parent


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

        test_provider = Provider()
        test_provider.lastName = 'Test_LastName'
        test_provider.firstName = 'Test_FirstName'
        test_provider.password = 'Test_Password'
        test_provider.email = 'provider@test.com'
        test_provider.schoolName = 'Test_schoolName'
        test_provider.put()
        self.test_provider = test_provider

        test_parent = Parent()
        test_parent.first_name = "Parent first name"
        test_parent.last_name = "Parent last name"
        test_parent.email = "parent@test.com"
        test_parent.password = "test_password"
        test_parent.put()
        self.test_parent = test_parent

        test_child = Child()
        test_child.first_name = "Test_ChildFirstName"
        test_child.last_name = "Test_ChildLastName"
        test_child.parent_key = test_parent.key
        test_child.parent_email = test_parent.email
        test_child.put()
        self.test_child = test_child

        test_program = Program(parent=test_provider.key)
        test_program.fee = 10
        test_program.programName = "Test Program"
        test_program.billingFrequency = "monthly"
        test_program.startDate = datetime.strptime('05/22/2017', DATE_FORMAT)
        test_program.put()
        self.test_program = test_program

    def tearDown(self):
        self.testbed.deactivate()

    def test_validate_enrollment_date_with_empty_endDate(self):
        start_date = datetime.strptime('05/25/2017', DATE_FORMAT)
        end_date = datetime.strptime('07/22/2017', DATE_FORMAT)
        enrollment_util.validate_enrollment_date(self.test_program, start_date, end_date)

    def test_validate_enrollment_date_with_empty_endDate_startDateTooEarly(self):
        start_date = datetime.strptime('05/20/2017', DATE_FORMAT)
        end_date = datetime.strptime('07/22/2017', DATE_FORMAT)
        with self.assertRaises(JoobaliRpcException):
            enrollment_util.validate_enrollment_date(self.test_program, start_date, end_date)

    def test_validate_enrollment_date(self):
        test_program = Program(parent=self.test_provider.key)
        test_program.fee = 10
        test_program.programName = "Test Program"
        test_program.billingFrequency = "monthly"
        test_program.startDate = datetime.strptime('05/22/2017', DATE_FORMAT)
        test_program.endDate = datetime.strptime('05/22/2018', DATE_FORMAT)
        test_program.put()

        start_date = datetime.strptime('05/23/2017', DATE_FORMAT)
        end_date = datetime.strptime('01/22/2018', DATE_FORMAT)
        enrollment_util.validate_enrollment_date(test_program, start_date, end_date)

    def test_validate_enrollment_date_startDateTooEarly(self):
        test_program = Program(parent=self.test_provider.key)
        test_program.fee = 10
        test_program.programName = "Test Program"
        test_program.billingFrequency = "monthly"
        test_program.startDate = datetime.strptime('05/22/2017', DATE_FORMAT)
        test_program.endDate = datetime.strptime('05/22/2018', DATE_FORMAT)
        test_program.put()

        start_date = datetime.strptime('05/20/2017', DATE_FORMAT)
        end_date = datetime.strptime('01/22/2018', DATE_FORMAT)
        with self.assertRaises(JoobaliRpcException):
            enrollment_util.validate_enrollment_date(test_program, start_date, end_date)

    def test_validate_enrollment_date_endDateTooLate(self):
        test_program = Program(parent=self.test_provider.key)
        test_program.fee = 10
        test_program.programName = "Test Program"
        test_program.billingFrequency = "monthly"
        test_program.startDate = datetime.strptime('05/22/2017', DATE_FORMAT)
        test_program.endDate = datetime.strptime('05/22/2018', DATE_FORMAT)
        test_program.put()

        start_date = datetime.strptime('05/20/2017', DATE_FORMAT)
        end_date = datetime.strptime('05/23/2018', DATE_FORMAT)
        with self.assertRaises(JoobaliRpcException):
            enrollment_util.validate_enrollment_date(test_program, start_date, end_date)

    def test_upsert_enrollment(self):
        test_enrollment_input = {
            'provider_key': self.test_provider.key,
            'child_key': self.test_child.key,
            'program_key': self.test_program.key,
            'status': 'initialized',
            'start_date': '05/25/2017',
            'end_date': '',
            'waive_registration': True
        }

        new_enrollment, invoice = enrollment_util.upsert_enrollment(test_enrollment_input)
        self.assertEqual('initialized', new_enrollment.status)


if __name__ == '__main__':
    unittest.main()
