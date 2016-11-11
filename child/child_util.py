from models import Child
from google.appengine.ext import ndb


def add_child(child_input, parent_id):
    """Input should be a dict containing all the Child Model's data"""
    parent_key = ndb.Key('Parent', parent_id)
    child = Child(parent=parent_key)
    child.first_name = child_input['first_name']
    child.last_name = child_input['last_name']
    child.date_of_birth = child_input['date_of_birth']
    child.put()
    return child


def update_child(child_input, parent_id, child_id):
    child = None
    return child
