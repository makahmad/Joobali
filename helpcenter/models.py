from google.appengine.ext import ndb

class Help(ndb.Model):
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    phone = ndb.StringProperty()
    comments = ndb.StringProperty(required=True)
    date_created = ndb.DateProperty(required=True)