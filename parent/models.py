from google.appengine.ext import ndb


class Parent(ndb.Model):
    """Model definition of a Parent"""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    date_of_birth = ndb.DateProperty()
    # email should be unique, but we must not rely on it
    email = ndb.StringProperty()
