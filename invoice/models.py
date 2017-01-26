from google.appengine.ext import ndb

class Invoice(ndb.Model):
    child_key = ndb.KeyProperty(required=True)
    provider_key = ndb.KeyProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    due_date = ndb.DateProperty(required=True)
    # provider info
    provider_email = ndb.StringProperty(required=True)
    provider_phone = ndb.StringProperty()
    # child info
    child_first_name = ndb.StringProperty(required=True)
    child_last_name = ndb.StringProperty(required=True)
    parent_email= ndb.StringProperty(required=True)
    # other
    date_created = ndb.DateProperty(required=True)
    paid = ndb.BooleanProperty(required=True, default=False)
    email_sent = ndb.BooleanProperty(required=True, default=False)
    autopay_source_id = ndb.StringProperty() # come from enrollment

class InvoiceLineItem(ndb.Model):
    enrollment_key = ndb.KeyProperty(required=True)
    invoice_key = ndb.KeyProperty(required=True)
    program_name = ndb.StringProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    start_date = ndb.DateProperty(required=True)
    end_date = ndb.DateProperty(required=True)

class InvoiceAdjustment(ndb.Model):
    invoice_key = ndb.KeyProperty(required=True)
    reason = ndb.StringProperty(required=True)
    amount = ndb.FloatProperty(required=True)