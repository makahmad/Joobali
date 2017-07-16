from google.appengine.ext import ndb

class FeeRate(ndb.Model):
	provider_key = ndb.KeyProperty(required=True)
	rate = ndb.FloatProperty(required=True) # Transaction Amount * rate = fee
	promotion_code = ndb.StringProperty()
