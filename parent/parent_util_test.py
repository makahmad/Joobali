import unittest

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from login.models import Provider
from parent import parent_util


class ParentUtilTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Create a consistency policy that will simulate the High Replication
        # consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
            probability=0)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        # Initialize memcache stub too, since ndb also uses memcache
        self.testbed.init_memcache_stub()
        # Clear in-context cache before each test.
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def test_setup_parent_for_child_ParentNotExist(self):
        # Arrange
        test_email = "test@email.com"
        test_child_first_name = "test"
        provider = Provider()

        # Act
        parent, verification_token = parent_util.setup_parent_for_child(email=test_email, provider_key=provider.key,
                                                                        child_first_name=test_child_first_name)

        # Assert
        self.assertEqual('invited', parent.status.status)
        self.assertEqual('parent_signup', verification_token.type)

    def test_setup_parent_for_child_ParentExist(self):
        # Arrange
        test_email = 'test@email.com'
        test_child_first_name_1 = 'test'
        test_child_first_name_2 = 'test2'
        provider = Provider()
        parent_1, verification_token = parent_util.setup_parent_for_child(email=test_email, provider_key=provider.key,
                                                                          child_first_name=test_child_first_name_1)
        # Act
        parent_2, verification_token = parent_util.setup_parent_for_child(email=test_email, provider_key=provider.key,
                                                                          child_first_name=test_child_first_name_2)
        self.assertEqual(parent_1, parent_2)
        self.assertEqual(None, verification_token)

if __name__ == '__main__':
    unittest.main()
