from google.appengine.ext import ndb

class Invoice(ndb.Model):
    parent_key = ndb.KeyProperty(required=True)
    provider_key = ndb.KeyProperty(required=True)
    amount = ndb.FloatProperty(required=True)

class InvoiceLineItem(ndb.Model):
    enrollment_key = ndb.KeyProperty(required=True)
    invoice_key = ndb.KeyProperty(required=True)
    amount = ndb.FloatProperty(required=True)