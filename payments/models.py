from google.appengine.ext import ndb

class Payment(ndb.Model):
    child_key = ndb.KeyProperty(required=True)
    provider_key = ndb.KeyProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    payer = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=False)
    date = ndb.DateProperty(required=True)