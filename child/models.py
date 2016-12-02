from google.appengine.ext import ndb


class Child(ndb.Model):
    """Model definition of a Child object"""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    parent_email = ndb.StringProperty()
    date_of_birth = ndb.DateProperty()


class ProviderChildView(ndb.Model):
    """Model definition of a provider-child view relationship"""
    provider_key = ndb.KeyProperty()
    child_key = ndb.KeyProperty()