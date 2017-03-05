from google.appengine.ext import ndb

class Referral(ndb.Model):
	schoolName = ndb.StringProperty(required=True)
	schoolEmail = ndb.StringProperty(required=True)
	schoolPhone = ndb.StringProperty()
	referrerName = ndb.StringProperty(required=True)
