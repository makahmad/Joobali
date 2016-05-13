from google.appengine.ext import ndb

class Provider(ndb.Model):
	firstName = ndb.StringProperty(required=True)
	lastName = ndb.StringProperty(required=True)
	schoolName = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	phone = ndb.StringProperty()
	website = ndb.StringProperty()
	license = ndb.StringProperty()
