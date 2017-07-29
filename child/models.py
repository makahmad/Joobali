from google.appengine.ext import ndb
from parent.models import Parent
from login.models import Provider
from datetime import datetime


class Child(ndb.Model):
    """
        Model definition of a Child object.
        A child can be uniquely identified by a Child.id
    """
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    parent_email = ndb.StringProperty(required=True)
    date_of_birth = ndb.DateProperty(required=False)
    parent_key = ndb.KeyProperty(kind=Parent, required=True)

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def generate_key(cls, child_id):
        return ndb.Key(cls.__name__, child_id)

    @classmethod
    def generate_child_entity(cls, first_name, last_name, date_of_birth, parent_email):
        child = Child(id=Child.get_next_available_id())
        child.first_name = first_name
        child.last_name = last_name
        if date_of_birth:
            child.date_of_birth = datetime.strptime(date_of_birth, "%m/%d/%Y").date()
        child.parent_email = parent_email
        return child

    @staticmethod
    def get_next_available_id():
        counter = ChildIdCounter.get_by_id("ChildIdCounter")
        if counter:
            child_id = counter.current_available_id
            counter.current_available_id += 1
            counter.put()
        else:
            child_id = 1  # TODO(rongjian): think about continue with the currently max id number
            counter = ChildIdCounter(id="ChildIdCounter")
            counter.current_available_id = 2
            counter.put()
        return child_id


class ChildIdCounter(ndb.Model):
    current_available_id = ndb.IntegerProperty(required=True)  # increment it after use in a transaction

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)

class ProviderChildView(ndb.Model):
    """
        Model definition of a provider-child view relationship
    """
    provider_key = ndb.KeyProperty(kind=Provider)
    child_key = ndb.KeyProperty(kind=Child)

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def generate_key(cls, provider_child_view_id):
        return ndb.Key(cls.__name__, provider_child_view_id)

    @classmethod
    def query_by_child_id(cls, child_id):
        return cls.query(cls.child_key == Child.generate_key(child_id))

    @classmethod
    def query_by_provider_id(cls, provider_id):
        return cls.query(cls.provider_key == Provider.generate_key(provider_id))
