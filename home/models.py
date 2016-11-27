from google.appengine.ext import ndb

# Whether the user has finished the init setup flow
class InitSetupStatus(ndb.Model):
	email = ndb.StringProperty(required=True)
	setupFinished = ndb.BooleanProperty()