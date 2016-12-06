from google.appengine.ext import ndb
from child.models import Child
from manageprogram.models import Program

class Enrollment(ndb.Model):
    """
        Enrollment is a child category of Provider, and contains information about the child_key and program_key
    """
    # Key to Child Entity
    child_key = ndb.KeyProperty(kind=Child)
    # Key to Program Entity
    program_key = ndb.KeyProperty(kind=Program)
    # The enrollment status
    status = ndb.StringProperty()
    # Effective Start Date for the enrollment, might be helpful for computing invoice ?
    start_date = ndb.DateProperty()
