from google.appengine.ext import ndb
from child.models import Child
from login.models import Provider

class Payment(ndb.Model):
    child_key = ndb.KeyProperty(kind=Child, required=True)
    provider_key = ndb.KeyProperty(kind=Provider, required=True)
    provider_email = ndb.StringProperty(required=True)
    invoice_key = ndb.KeyProperty(required=False)
    amount = ndb.FloatProperty(required=True)
    payer = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=False)
    date = ndb.DateTimeProperty(required=True)
    date_created = ndb.DateTimeProperty(required=True)
    note = ndb.StringProperty(required=False) # Check number if payment = Check, Note if payment type = Other
    balance = ndb.FloatProperty(required=True)
