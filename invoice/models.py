from google.appengine.ext import ndb
from enrollment.models import Enrollment
from payments.models import Payment
from datetime import datetime, timedelta

class Invoice(ndb.Model):
    child_key = ndb.KeyProperty(required=True)
    provider_key = ndb.KeyProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    due_date = ndb.DateTimeProperty(required=True)
    # provider info
    provider_email = ndb.StringProperty(required=True)
    provider_phone = ndb.StringProperty()
    # child info
    child_first_name = ndb.StringProperty(required=True)
    child_last_name = ndb.StringProperty(required=True)
    parent_email= ndb.StringProperty(required=True)
    # other
    late_fee_enforced = ndb.BooleanProperty(default=True)
    status = ndb.StringProperty(required=True, default="NEW")
    # All possible status for a invoice
    _POSSIBLE_STATUS = {
        'NEW': 'NEW',
        'PROCESSING': 'PROCESSING',
        'COMPLETED': 'COMPLETED', # paid by parents
        'FAILED': 'FAILED',
        'CANCELLED': 'CANCELLED',
        'MARKED_PAID': 'MARKED_PAID', # marked paid by provider
        'PAID_OFFLINE': 'PAID_OFFLINE', # paid offline with case/check
        'DELETED': 'DELETED', # deleted by the provider
    }
    email_sent = ndb.BooleanProperty(required=True, default=False)
    send_email = ndb.BooleanProperty(required=True, default=True) # whether a email should be sent for this invoice
    autopay_source_id = ndb.StringProperty() # come from enrollment
    autopay_failure_message = ndb.StringProperty() # from dwolla
    dwolla_transfer_id = ndb.StringProperty() # The money transfer for the payment (funded_transfer)
    cancelled_transfer_ids = ndb.StringProperty(repeated=True) # The payments that were cancelled (funded_transfer)
    pdf = ndb.BlobProperty()

    general_note = ndb.StringProperty(default="")
    late_fee_note = ndb.StringProperty(default="")

    is_recurring = ndb.BooleanProperty(default=False) # is program recurring fee invoices

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)

    # due date is 23:59:99 of that day, so add another day to the due date (which is 00:00:00 of that day)
    def is_over_due(self, grace_days=0):
        return self.due_date + timedelta(days=1 + grace_days) < datetime.now() and (self.status == Invoice._POSSIBLE_STATUS['NEW']
                                                        or self.status == Invoice._POSSIBLE_STATUS['CANCELLED']
                                                        or self.status == Invoice._POSSIBLE_STATUS['FAILED'])

    def is_paid(self):
        return self.status == Invoice._POSSIBLE_STATUS['COMPLETED'] or self.status == Invoice._POSSIBLE_STATUS['MARKED_PAID'] or self.status == Invoice._POSSIBLE_STATUS['PAID_OFFLINE']

    def is_processing(self):
        return self.status == Invoice._POSSIBLE_STATUS['PROCESSING'] and self.dwolla_transfer_id != None

    def is_deleted(self):
        return self.status == Invoice._POSSIBLE_STATUS['DELETED']


class InvoiceLineItem(ndb.Model):
    enrollment_key = ndb.KeyProperty(kind=Enrollment)
    invoice_key = ndb.KeyProperty(kind=Invoice, required=True)
    program_name = ndb.StringProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    start_date = ndb.DateTimeProperty()
    end_date = ndb.DateTimeProperty()
    # Reason for adjustment
    description = ndb.StringProperty()

    payment_key = ndb.KeyProperty(kind=Payment)

    # Timestamps
    time_created = ndb.DateTimeProperty(auto_now_add=True)
    time_updated = ndb.DateTimeProperty(auto_now=True)