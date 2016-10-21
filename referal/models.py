from google.appengine.ext import ndb

class Referal(ndb.Model):
	schoolName = ndb.StringProperty(required=True)
	schoolEmail = ndb.StringProperty(required=True)
	schoolPhone = ndb.StringProperty()
	refererName = ndb.StringProperty(required=True)
