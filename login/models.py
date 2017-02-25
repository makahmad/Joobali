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

    @staticmethod
    def get_next_available_id():
        counter = ProviderIdCounter.get_by_id("ProviderIdCounter")
        id = 0
        if counter:
            id = counter.current_available_id
            counter.current_available_id = counter.current_available_id + 1
            counter.put()
        else:
            id = 1  # TODO(rongjian): think about continue with the currently max id number
            counter = ProviderIdCounter(id="ProviderIdCounter")
            counter.current_available_id = 2
            counter.put()
        return id

class ProviderIdCounter(ndb.Model):
    current_available_id = ndb.IntegerProperty(required=True) # increment it after use in a transaction


# The parent is the corresponding user object
class Unique(ndb.Model):
    # This is to be the id of Unique object
    email = ndb.StringProperty()

    # Reference to its attached object
    provider_key = ndb.KeyProperty(kind=Provider)
    parent_key = ndb.KeyProperty(kind=Parent)