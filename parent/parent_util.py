import time

from models import Parent, ParentInvitation, ParentStatus
from passlib.apps import custom_app_context as pwd_context
from login.models import Unique
from login import unique_util
from verification.models import VerificationToken


def setup_parent_for_child(email, provider_key, child_first_name):
    """
        Add a new Parent object with invitation info if the email is not yet used.
        Otherwise, return the existing Parent Entity.

        Input is expected to be
        {
            'email': email,
            'provider_key' : provider_key,
            'child_first_name' : child_name
        }
    """
    parent = Parent(id=Parent.get_next_available_id())
    existing_parent = get_parents_by_email(email)
    if existing_parent is None:
        parent.email = email

        # Generate invitation information
        parent_invitation = ParentInvitation()
        parent_invitation.child_first_name = child_first_name
        parent_invitation.provider_key = provider_key
        parent.invitation = parent_invitation

        # Generate status information
        parent_status = ParentStatus()
        parent_status.status = 'invited'
        parent.status = parent_status

        # Generate random initial password so that it can pass the 'required' check
        random_str = parent.email + str(time.time())
        parent.password = pwd_context.encrypt(random_str)

        parent.put()
        unique_util.upsert_parent(parent.email, parent.key)
        verification_token = VerificationToken.create_new_parent_signup_token(parent)
        verification_token.put()
        return parent, verification_token
    else:
        return existing_parent, None


def signup_invited_parent(email, salted_password, phone, first_name, last_name):
    parent = get_parents_by_email(email)
    parent.password = salted_password
    parent.first_name = first_name
    parent.last_name = last_name
    parent.phone = phone
    # Clean the invitation token to flag that the parent has registered
    parent.invitation.token = None
    parent.put()
    return parent


# TODO(zilong): Make this transactional
def get_parents_by_email(email):
    unique = Unique.generate_key(email).get()
    if unique is None or unique.parent_key is None:
        return None
    return unique.parent_key.get()


def get_parent_by_dwolla_id(customer_url):
    result = Parent.query(Parent.customerId == customer_url).fetch(1)
    if result:
        return result[0]
    return None
