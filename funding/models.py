from google.appengine.ext import ndb

class FeeRate(ndb.Model):
	provider_key = ndb.KeyProperty(required=True)
	rate = ndb.FloatProperty(required=True) # Transaction Amount * rate = fee
	promotion_code = ndb.StringProperty()

	# Timestamps
	time_created = ndb.DateTimeProperty(auto_now_add=True)
	time_updated = ndb.DateTimeProperty(auto_now=True)