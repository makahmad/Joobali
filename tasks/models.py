from google.appengine.ext import ndb

class DwollaEvent(ndb.Model):
    ''' Dwolla Events Registery object, used to keep track of which dwolla events has been recognized (notification email sent).
        Note invoice payment related dwolla transfer is kept by Invoice.dwolla_transfer_id '''
    event_id = ndb.StringProperty(required=True)
    event_content = ndb.StringProperty()

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)

class DwollaTokens(ndb.Model):
    ''' Dwolla tokens needed to make API calls to Dwolla. Needs to refresh every 1 hour.'''
    access_token = ndb.StringProperty(required=True)
    refresh_token = ndb.StringProperty(required=True)

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)