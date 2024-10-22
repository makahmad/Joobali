from google.appengine.ext import ndb


class ParentInvitation(ndb.Model):
    """
        ParentInvitation should only exist in a Parent entity.
        It's for grouping invitation related information
    """

    # Can't enforce kind=Provider because of the import loop. But this constraint should be assumed
    provider_key = ndb.KeyProperty()
    child_first_name = ndb.StringProperty()
    enrollment_key = ndb.KeyProperty()

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)


class ParentStatus(ndb.Model):
    status = ndb.StringProperty()

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)


class Parent(ndb.Model):
    """Model definition of a Parent"""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    # email should be unique, but we must not rely on it
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    phone = ndb.StringProperty()
    status = ndb.StructuredProperty(ParentStatus, repeated=False)
    invitation = ndb.StructuredProperty(ParentInvitation, repeated=False)

    tos_pp_accepted = ndb.BooleanProperty(default=False) # joobali/dwolla terms of service and privacy policy accepted

    is_deleted = ndb.BooleanProperty(default=False)

    # Dwolla customer id
    customerId = ndb.StringProperty()

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @classmethod
    def generate_key(cls, parent_id):
        return ndb.Key(cls.__name__, parent_id)

    @staticmethod
    def get_next_available_id():
        counter = ParentIdCounter.get_by_id("ParentIdCounter")
        if counter:
            parent_id = counter.current_available_id
            counter.current_available_id += 1
            counter.put()
        else:
            parent_id = 1  # TODO(rongjian): think about continue with the currently max id number
            counter = ParentIdCounter(id="ParentIdCounter")
            counter.current_available_id = 2
            counter.put()
        return parent_id


class ParentIdCounter(ndb.Model):
    current_available_id = ndb.IntegerProperty(required=True)  # increment it after use in a transaction

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)
