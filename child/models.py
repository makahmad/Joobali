from google.appengine.ext import ndb
from parent.models import Parent
from login.models import Provider


class Child(ndb.Model):
    """
        Model definition of a Child object.
        A child can be uniquely identified by a Child.id
    """
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    parent_email = ndb.StringProperty()
    date_of_birth = ndb.DateProperty()
    parent_key = ndb.KeyProperty(kind=Parent)

    @classmethod
    def generate_key(cls, child_id):
        return ndb.Key(cls.__name__, child_id)


class ProviderChildView(ndb.Model):
    """
        Model definition of a provider-child view relationship
    """
    provider_key = ndb.KeyProperty(kind=Provider)
    child_key = ndb.KeyProperty(kind=Child)

    @classmethod
    def generate_key(cls, provider_child_view_id):
        return ndb.Key(cls.__name__, provider_child_view_id);
