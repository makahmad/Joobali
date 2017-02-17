from google.appengine.ext import ndb

from parent.models import Parent


class Provider(ndb.Model):
    firstName = ndb.StringProperty(required=True)
    lastName = ndb.StringProperty(required=True)
    schoolName = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    phone = ndb.StringProperty()
    website = ndb.StringProperty()
    license = ndb.StringProperty()
    # Additional fields for Dwolla verified customer.
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    postalCode = ndb.StringProperty()
    dateOfBirth = ndb.DateProperty()
    # Only last four digits is required
    ssn = ndb.StringProperty()

    # Dwolla customer id
    customerId = ndb.StringProperty()

    # General Invoice Related Fields
    graceDays = ndb.IntegerProperty(default=0)
    lateFee = ndb.FloatProperty(default=0.0)

    @classmethod
    def generate_key(cls, provider_id):
        return ndb.Key(cls.__name__, provider_id)

# The parent is the corresponding user object
class Unique(ndb.Model):
    # This is to be the id of Unique object
    email = ndb.StringProperty()

    # Reference to its attached object
    provider_key = ndb.KeyProperty(kind=Provider)
    parent_key = ndb.KeyProperty(kind=Parent)