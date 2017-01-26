from google.appengine.ext import ndb


class Parent(ndb.Model):
    """Model definition of a Parent"""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    # email should be unique, but we must not rely on it
    email = ndb.StringProperty()
    password = ndb.StringProperty(required=True)

    # Dwolla customer id
    customerId = ndb.StringProperty()
