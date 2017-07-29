from google.appengine.ext import ndb


# Whether the user has finished the init setup flow
class InitSetupStatus(ndb.Model):
	email = ndb.StringProperty(required=True)
	setupFinished = ndb.BooleanProperty()

	# Timestamps
	time_created = ndb.DateTimeProperty(auto_now_add=True)
	time_updated = ndb.DateTimeProperty(auto_now=True)