from google.appengine.ext import ndb

class Notification(ndb.Model):
    parent_key = ndb.KeyProperty()
    provider_key = ndb.KeyProperty()
    child_key = ndb.KeyProperty()

    enrollment_key = ndb.KeyProperty()
    invoice_key = ndb.KeyProperty()
    payment_key = ndb.KeyProperty()

    # other
    type = ndb.StringProperty(required=True, default="UNKNOWN")
    # All possible type for a notification
    _POSSIBLE_TYPE = {
        'UNKNOWN': 'UNKNOWN',
        'CHILD': 'CHILD',
        'BANK': 'BANK',
        'INVOICE': 'INVOICE',
    }
    action_required = ndb.BooleanProperty(required=True, default=False)
    action_done = ndb.BooleanProperty(required=True, default=False)
    notification_viewed = ndb.BooleanProperty(required=True, default=False)