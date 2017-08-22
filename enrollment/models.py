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
    # Effective Start Date for the billing, used for computing invoice.
    start_date = ndb.DateTimeProperty()
    # Effective End Date for the billing, used for computing invoice. If null, it means this enrollment will never end
    end_date = ndb.DateTimeProperty()
    # Overriding Billing Fee
    billing_fee = ndb.FloatProperty();
    # Autopay funding source. If set, the related invoice will be automatically paid by this source.
    autopay_source_id = ndb.StringProperty()
    # Number of resent emails sent for enrollment
    resent_email_count = ndb.IntegerProperty(default=0)
    # Autopay # of days before the due date
    pay_days_before = ndb.IntegerProperty(default=0)
    # Whether to waive or not waive registration fee for the first invoice
    waive_registration = ndb.BooleanProperty()
    # All possible status for an enrollment
    _POSSIBLE_STATUS = {
        'initialized',
        'invited',
        'active',
        'payment resolve pending',
        'inactive',
        'expired'}

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)

    def can_resend_invitation(self):
        return self.status in {'initialized', 'invited'}

    def is_active(self):
        return self.status in {'active'}

    @classmethod
    def generate_key(cls, provider_id, enrollment_id):
        return ndb.Key(Provider.__name__, int(provider_id), cls.__name__, int(enrollment_id))

    @classmethod
    def get(cls, provider_id, enrollment_id):
        return cls.generate_key(provider_id, enrollment_id).get()

    @classmethod
    def get_possible_status(cls):
        return cls._POSSIBLE_STATUS.copy()
