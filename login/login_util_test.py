import unittest

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import testbed, ndb
from passlib.apps import custom_app_context as pwd_context

from login.login_util import provider_login, parent_login
from login.models import Provider, ProviderStatus
from parent import parent_util


class LoginViewTestCase(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        # Initialize memcache stub too, since ndb also uses memcache
        self.testbed.init_memcache_stub()
        # Clear in-context cache before each test.
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    # TODO(zilong): use the provider signup function to create test provider
    def create_test_provider(self, status, email, password):
        provider = Provider()
        provider.password = pwd_context.encrypt(password)
        provider.email = email
        providerStatus = ProviderStatus()
        providerStatus.status = status
        provider.status = providerStatus
        provider.firstName = "firstName"
        provider.lastName = "lastName"
        provider.customerId = "fakeCustomerId"
        provider.schoolName = "fakeSchool"
        provider.put()
        return provider

    def create_test_parent(self, provider, email):
        return parent_util.setup_parent_for_child(email=email, provider_key=provider.key,
                                                  child_first_name="fake_child_first_name")

    def signup_parent(self, email, password):
        return parent_util.signup_invited_parent(email=email, salted_password=pwd_context.encrypt(password),
                                                 phone="fakePhone", first_name="ParentFirstName",
                                                 last_name="ParentLastName")

    def test_provider_login_not_yet_exist(self):
        email = 'fake@provider.com'
        password = 'fakePassword'
        login_result = provider_login(email, password)

        self.assertFalse(login_result.is_succeeded())
        self.assertEqual("Error: user with that email does not exist", login_result.error_msg)

    def test_provider_login_not_yet_verify_email(self):
        email = 'fake@provider.com'
        password = 'fakePassword'
        self.create_test_provider('signup', email, password)

        login_result = provider_login(email, password)

        self.assertFalse(login_result.is_succeeded())
        self.assertEqual("Error: provider has not yet verified email", login_result.error_msg)

    def test_provider_login_password_incorrect(self):
        email = 'fake@provider.com'
        password = 'fakePassword'
        self.create_test_provider('active', email, password)
        wrongPassword = password + "haha"
        login_result = provider_login(email, wrongPassword)

        self.assertFalse(login_result.is_succeeded())
        self.assertEqual("Error: wrong combination of credential", login_result.error_msg)

    def test_provider_login_succeeded(self):
        email = 'fake@provider.com'
        password = 'fakePassword'
        provider = self.create_test_provider('active', email, password)
        login_result = provider_login(email, password)

        self.assertTrue(login_result.is_succeeded())
        self.assertEqual(email, login_result.email)
        self.assertEqual("firstName lastName", login_result.name)
        self.assertEqual(provider.key.id(), login_result.user_id)
        self.assertEqual(provider.customerId, login_result.dwolla_customer_url)

    def test_parent_login_not_yet_exist(self):
        email = 'fake@parent.com'
        password = 'fakeParentPassword'

        login_result = parent_login(email, password)

        self.assertFalse(login_result.is_succeeded())
        self.assertEqual("Error: user with that email does not exist", login_result.error_msg)

    def test_parent_login_not_yet_signup(self):
        provider = self.create_test_provider('signup', 'fake@provider.com', 'fakePassword')
        email = 'fake@parent.com'
        password = 'fakeParentPassword'
        self.create_test_parent(provider, email)

        login_result = parent_login(email, password)

        self.assertFalse(login_result.is_succeeded())
        self.assertEqual("Error: parent has not yet signed up", login_result.error_msg)

    def test_parent_login_password_incorrect(self):
        provider = self.create_test_provider('signup', 'fake@provider.com', 'fakePassword')
        email = 'fake@parent.com'
        password = 'fakeParentPassword'
        self.create_test_parent(provider, email)
        self.signup_parent(email, password)

        wrongPassword = password + "haha"
        login_result = parent_login(email, wrongPassword)

        self.assertFalse(login_result.is_succeeded())
        self.assertEqual("Error: wrong combination of credential", login_result.error_msg)

    def test_parent_login_succeeded(self):
        provider = self.create_test_provider('signup', 'fake@provider.com', 'fakePassword')
        email = 'fake@parent.com'
        password = 'fakeParentPassword'
        self.create_test_parent(provider, email)
        parent = self.signup_parent(email, password)

        login_result = parent_login(email, password)

        self.assertTrue(login_result.is_succeeded())
        self.assertEqual(parent.email, login_result.email)
        self.assertEqual("ParentFirstName ParentLastName", login_result.name)
        self.assertEqual(parent.key.id(), login_result.user_id)
        self.assertEqual(parent.customerId, login_result.dwolla_customer_url)
