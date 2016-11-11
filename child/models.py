from google.appengine.ext import ndb


class Child(ndb.Model):
    """Model definition of a Child object"""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    date_of_birth = ndb.DateProperty()
