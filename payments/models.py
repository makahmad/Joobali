from google.appengine.ext import ndb
from child.models import Child
from login.models import Provider

class Payment(ndb.Model):
    child_key = ndb.KeyProperty(kind=Child, required=True)
    provider_key = ndb.KeyProperty(kind=Provider, required=True)
    provider_email = ndb.StringProperty(required=True)
    invoice_key = ndb.KeyProperty(required=False)
    amount = ndb.FloatProperty(required=True)
    fee = ndb.FloatProperty(required=True, default=0.0) # for online transfer
    payer = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=False) # 'Oneline Transfer', "Check", "Cash" e.t.c.
    date = ndb.DateTimeProperty(required=True)
    note = ndb.StringProperty(required=False) # Check number if payment = Check, Note if payment type = Other
    balance = ndb.FloatProperty(required=True)

    dwolla_transfer_id = ndb.StringProperty() # The money transfer for the payment (funded_transfer)
    status = ndb.StringProperty(required=False) # status for online payments

    is_deleted = ndb.BooleanProperty(default=False)

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)