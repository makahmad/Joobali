from google.appengine.ext import ndb
from enrollment.models import Enrollment
from payments.models import Payment
from datetime import date

class Invoice(ndb.Model):
    child_key = ndb.KeyProperty(required=True)
    provider_key = ndb.KeyProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    due_date = ndb.DateProperty(required=True)
    # provider info
    provider_email = ndb.StringProperty(required=True)
    provider_phone = ndb.StringProperty()
    # child info
    child_first_name = ndb.StringProperty(required=True)
    child_last_name = ndb.StringProperty(required=True)
    parent_email= ndb.StringProperty(required=True)
    # other
    date_created = ndb.DateProperty(required=True)
    status = ndb.StringProperty(required=True, default="NEW")
    # All possible status for a invoice
    _POSSIBLE_STATUS = {
        'NEW': 'NEW',
        'PROCESSING': 'PROCESSING',
        'COMPLETED': 'COMPLETED', # paid by parents
        'FAILED': 'FAILED',
        'MARKED_PAID': 'MARKED_PAID', # marked paid by provider
        'PAID_OFFLINE': 'PAID_OFFLINE', # paid offline with case/check
    }
    email_sent = ndb.BooleanProperty(required=True, default=False)
    autopay_source_id = ndb.StringProperty() # come from enrollment
    dwolla_transfer_id = ndb.StringProperty() # The money transfer for the payment
    pdf = ndb.BlobProperty()


    def is_late(self):
        return self.due_date < date.today()

    def is_paid(self):
        return self.status == Invoice._POSSIBLE_STATUS['COMPLETED'] or self.status == Invoice._POSSIBLE_STATUS['MARKED_PAID'] or self.status == Invoice._POSSIBLE_STATUS['PAID_OFFLINE']

class InvoiceLineItem(ndb.Model):
    enrollment_key = ndb.KeyProperty(kind=Enrollment)
    invoice_key = ndb.KeyProperty(kind=Invoice, required=True)
    program_name = ndb.StringProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    start_date = ndb.DateProperty()
    end_date = ndb.DateProperty()
    # Reason for adjustment
    description = ndb.StringProperty()

    payment_key = ndb.KeyProperty(kind=Payment)