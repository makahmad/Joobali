from google.appengine.ext import ndb

from parent.models import Parent


class ProviderStatus(ndb.Model):
    _POSSIBLE_STATUS = {'signup', 'active'}
    status = ndb.StringProperty()


class FailedBetaLogins(ndb.Model):
    firstName = ndb.StringProperty()
    lastName = ndb.StringProperty()
    schoolName = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    license = ndb.StringProperty()
    date = ndb.DateProperty()
    IP = ndb.StringProperty()
    beta_code = ndb.StringProperty()

class Provider(ndb.Model):
    firstName = ndb.StringProperty(required=True)
    lastName = ndb.StringProperty(required=True)
    schoolName = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)

    status = ndb.StructuredProperty(ProviderStatus, repeated=False)

    tos_pp_accepted = ndb.BooleanProperty(default=False) # joobali/dwolla terms of service and privacy policy accepted

    phone = ndb.StringProperty()
    website = ndb.StringProperty()
    license = ndb.StringProperty()
    tin = ndb.StringProperty()
    logo = ndb.BlobProperty()
    showLogo = ndb.BooleanProperty(default=False) # used to decide whether to show logo on the profile page

    # Additional fields for Dwolla verified customer.
    addressLine1 = ndb.StringProperty()
    addressLine2 = ndb.StringProperty() # address line 2 (optional)
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    zipcode = ndb.StringProperty()
    dateOfBirth = ndb.DateProperty()
    # Only last four digits is required
    ssn = ndb.StringProperty()

    # Dwolla customer id
    customerId = ndb.StringProperty()
    # Dwolla funding source to receive money
    default_funding_source = ndb.StringProperty()

    # General Invoice Related Fields
    graceDays = ndb.IntegerProperty(default=0)
    lateFee = ndb.FloatProperty(default=0.0)
    lateFeeInvoiceNote = ndb.StringProperty()
    generalInvoiceNote = ndb.StringProperty()


    @staticmethod
    def get_next_available_id():
        counter = ProviderIdCounter.get_by_id("ProviderIdCounter")
        if counter:
            provider_id = counter.current_available_id
            counter.current_available_id += 1
            counter.put()
        else:
            provider_id = 1  # TODO(rongjian): think about continue with the currently max id number
            counter = ProviderIdCounter(id="ProviderIdCounter")
            counter.current_available_id = 2
            counter.put()
        return provider_id

    @classmethod
    def generate_key(cls, provider_id):
        return ndb.Key(cls.__name__, provider_id)


class ProviderIdCounter(ndb.Model):
    current_available_id = ndb.IntegerProperty(required=True)  # increment it after use in a transaction


# The parent is the corresponding user object
class Unique(ndb.Model):
    # This is to be the id of Unique object
    email = ndb.StringProperty()

    # Reference to its attached object
    provider_key = ndb.KeyProperty(kind=Provider)
    parent_key = ndb.KeyProperty(kind=Parent)

    @classmethod
    def generate_key(cls, email):
        return ndb.Key(cls.__name__, email)
