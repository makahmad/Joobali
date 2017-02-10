from google.appengine.ext import ndb
from child.models import Child
from manageprogram.models import Program
from login.models import Provider

class Enrollment(ndb.Model):
    """
        Enrollment is a child category of Provider, and contains information about the child_key and program_key
        You will need a (provider_id, enrollment_id) pair to uniquely identify an enrollment
        TODO(zilong): (provider_id, program_id, child_id) should also uniquely identify an enrollment
    """
    # Key to Child Entity
    child_key = ndb.KeyProperty(kind=Child)
    # Key to Program Entity
    program_key = ndb.KeyProperty(kind=Program)
    # The enrollment status
    status = ndb.StringProperty()
    # Effective Start Date for the enrollment, might be helpful for computing invoice ?
    start_date = ndb.DateProperty()
    # Autopay funding source. If set, the related invoice will be automatically paid by this source.
    autopay_source_id = ndb.StringProperty()

    @classmethod
    def generate_key(cls, provider_id, enrollment_id):
        return ndb.Key(Provider.__name__, provider_id, cls.__name__, enrollment_id)
