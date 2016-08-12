from google.appengine.ext import ndb

class Funding(ndb.Model):
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty(required=True)
	accountNumber = ndb.StringProperty(required=True)
	routingNumber = ndb.StringProperty(required=True)
