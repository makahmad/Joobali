from google.appengine.ext import ndb


class Enrollment(ndb.Model):
    child_first_name = ndb.StringProperty()
    child_last_name = ndb.StringProperty()
    parent_first_name = ndb.StringProperty()
    parent_last_name = ndb.StringProperty()
    status = ndb.StringProperty()
    email = ndb.StringProperty()
    # Key to the Program Entity
    program_id = ndb.StringProperty()
