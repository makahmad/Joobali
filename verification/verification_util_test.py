import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from parent.models import Parent
from verification import verification_util
from verification.models import VerificationToken


class VerificationUtilTestCase(unittest.TestCase):

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

    def test_get_parent_signup_verification_token_with_token_id(self):
        # Arrange
        test_email = 'test@parent.com'
        test_password = 'test_password'
        parent = Parent(id=1)
        parent.email = test_email
        parent.password = test_password
        parent.put()
        expected_token = VerificationToken.create_new_parent_signup_token(parent)
        expected_token.put()

        # Act
        actual_token = verification_util.get_parent_signup_verification_token(token_id=expected_token.key.id())

        # Assert
        self.assertEqual(expected_token, actual_token)

    def test_get_parent_signup_verification_token_with_parent_key(self):
        # Arrange
        test_email = 'test@parent.com'
        test_password = 'test_password'
        parent = Parent(id=1)
        parent.email = test_email
        parent.password = test_password
        parent.put()
        expected_token1 = VerificationToken.create_new_parent_signup_token(parent)
        expected_token1.put()
        expected_token2 = VerificationToken.create_new_parent_signup_token(parent)
        expected_token2.put()

        # Act
        actual_tokens = verification_util.get_parent_signup_verification_token(parent_key=parent.key)

        # Assert
        self.assertEqual(2, len(actual_tokens))
        self.assertIn(expected_token1, actual_tokens)
        self.assertIn(expected_token2, actual_tokens)


