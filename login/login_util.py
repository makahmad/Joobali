import logging
from passlib.apps import custom_app_context as pwd_context

from login.models import Provider
from parent.models import Parent

logger = logging.getLogger(__name__)


class LoginResult:
    """
    This class contains the result of a login attempt.
    Attributes:
        status(str)
        email(str)
        name(str)
        is_provider(bool)
        dwolla_customer_url(str)
        user_id(str or int)
        error_msg(str)
    """

    def __init__(self):
        self.status = None
        self.password_verified = None
        self.email = None
        self.name = None
        self.is_provider = None
        self.dwolla_customer_url = None
        self.user_id = None
        self.error_msg = None

    def is_succeeded(self):
        return self.status == "Succeeded"


def provider_login(email, password):
    login_result = LoginResult()
    login_result.status = "Failed"

    query = Provider.query().filter(Provider.email == email)
    provider = query.get()

    if provider is None:
        login_result.error_msg = 'Error: user with that email does not exist'
        return login_result

    if provider.status.status != 'active':
        logger.info('Error: provider has not yet verified email')
        login_result.error_msg = 'Error: provider has not yet verified email'
        return login_result

    if pwd_context.verify(password, provider.password):
        login_result.status = "Succeeded"
        login_result.email = provider.email
        login_result.name = provider.firstName + ' ' + provider.lastName
        login_result.user_id = provider.key.id()
        login_result.dwolla_customer_url = provider.customerId
        login_result.is_provider = True
    else:
        login_result.error_msg = "Error: wrong combination of credential"

    return login_result


def parent_login(email, password):
    login_result = LoginResult()
    login_result.status = "Failed"

    query = Parent.query().filter(Parent.email == email)
    parent = query.get()

    if parent is None:
        login_result.error_msg = 'Error: user with that email does not exist'
        return login_result

    if parent.status.status != 'active':
        logger.info('Error: parent has not yet signed up')
        login_result.error_msg = 'Error: parent has not yet signed up'
        return login_result

    if pwd_context.verify(password, parent.password):
        login_result.status = "Succeeded"
        login_result.email = parent.email
        login_result.name = parent.first_name + ' ' + parent.last_name
        login_result.user_id = parent.key.id()
        login_result.dwolla_customer_url = parent.customerId
        login_result.is_provider = False
    else:
        login_result.error_msg = "Error: wrong combination of credential"

    return login_result
