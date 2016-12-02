from google.appengine.ext import ndb


class Enrollment(ndb.Model):
    """Enrollment should be keyed with program id and provider id"""
    # Key to Child Entity
    child_key = ndb.KeyProperty()
    # Key to Program Entity
    program_key = ndb.KeyProperty()
    # The enrollment status
    status = ndb.StringProperty()
    # Effective Start Date for the enrollment, might be helpful for computing invoice ?
    start_date = ndb.DateProperty()
