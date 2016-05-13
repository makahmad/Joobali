from google.appengine.ext import ndb

class Referal(ndb.Model):
	schoolName = ndb.StringProperty(required=True)
	schoolAdmin = ndb.StringProperty(required=True)
	schoolAdminEmail = ndb.StringProperty(required=True)
	schoolPhone = ndb.StringProperty()
	refererEmail = ndb.StringProperty()
	note = ndb.TextProperty(indexed=False)
