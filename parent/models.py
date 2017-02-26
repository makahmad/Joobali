from google.appengine.ext import ndb


class Parent(ndb.Model):
    """Model definition of a Parent"""
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    # email should be unique, but we must not rely on it
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    # this is the password generated by the system before the parent actually signs up
    temp_password = ndb.StringProperty()
    phone = ndb.StringProperty()

    # Dwolla customer id
    customerId = ndb.StringProperty()

    @staticmethod
    def get_next_available_id():
        counter = ParentIdCounter.get_by_id("ParentIdCounter")
        id = 0
        if counter:
            id = counter.current_available_id
            counter.current_available_id = counter.current_available_id + 1
            counter.put()
        else:
            id = 1  # TODO(rongjian): think about continue with the currently max id number
            counter = ParentIdCounter(id="ParentIdCounter")
            counter.current_available_id = 2
            counter.put()
        return id

class ParentIdCounter(ndb.Model):
    current_available_id = ndb.IntegerProperty(required=True) # increment it after use in a transaction
