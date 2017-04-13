from google.appengine.ext import ndb
from child.models import Child
from login.models import Provider

class Payment(ndb.Model):
    child_key = ndb.KeyProperty(kind=Child, required=True)
    provider_key = ndb.KeyProperty(kind=Provider, required=True)
    provider_email = ndb.StringProperty(required=True)
    program_id = ndb.FloatProperty(required=False)
    amount = ndb.FloatProperty(required=True)
    payer = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=False)
    date = ndb.DateProperty(required=True)
    date_created = ndb.DateProperty(required=True)
    note = ndb.StringProperty(required=False)
    balance = ndb.FloatProperty(required=True)
