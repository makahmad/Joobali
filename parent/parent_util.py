from models import Parent
from passlib.apps import custom_app_context as pwd_context
import base64
import random

def add_parent_for_child(parent_input):
    """Add a new parent object"""
    parent = Parent()
    existing_parent = get_parents_by_email(parent_input["email"])
    if existing_parent is None:
        parent.email = parent_input["email"]
        password = base64.b64encode(bytes([random.getrandbits(64)]))
        parent.temp_password = password
        parent.password = pwd_context.encrypt(password)
        parent.put()
        return parent
    else:
        return existing_parent


def get_parents_by_email(email):
    qry = Parent.query(Parent.email == email)
    for parent in qry.fetch():
        return parent
