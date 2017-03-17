from models import Parent
from models import ParentInvitation
from passlib.apps import custom_app_context as pwd_context
from login.models import Unique
from login import unique_util
import time
import hashlib


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
        random_str = parent.email + str(time.time())
        parent_invitation.token = hashlib.md5(random_str).hexdigest()
        parent_invitation.child_first_name = child_first_name
        parent_invitation.provider_key = provider_key
        parent_invitation.link = '?m=%s&t=%s' % (email, parent_invitation.token)

        parent.invitation = parent_invitation
        parent.password = pwd_context.encrypt(parent_invitation.token)
        parent.put()
        # TODO(zilong): handle possible email existing exception
        unique_util.upsert_parent(parent.email, parent.key)
        return parent
    else:
        return existing_parent


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


def invite_parent_for_enrollment(parent, enrollment):
    parent.invitation.enrollment_key = enrollment.key
    parent.put()


# TODO(zilong): Implement this
def notify_parent_for_enrollment(parent, enrollment):
    pass


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

def verify_invitation_token(email, invitation_token):
    parent = get_parents_by_email(email)
    if parent.invitation is None or parent.invitation.token is None:
        return False
    elif parent.invitation.token == invitation_token:
        return True
