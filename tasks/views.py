from django.http import HttpResponse
from enrollment import enrollment_util
from invoice import invoice_util
from parent import parent_util
from login.models import Provider
from google.appengine.ext import ndb


def invoice_calculation(request):
    print "INVOICE CALCULATION"
    # loop over providers...
    invoice_dict = dict()
    providers = Provider.query().fetch()
    for provider in providers:
        enrollments = enrollment_util.list_enrollment_by_provider(provider.key.id())
        for enrollment in enrollments:
            child_key = enrollment["child_key"]
            child = child_key.get()
            parent = parent_util.get_parents_by_email(child.parent_email)

            provider_parent_pair_key = provider.key.id() + str(parent.key.id()) # TODO: make parent key their email str
            invoice = None
            if provider_parent_pair_key in invoice_dict:
                invoice = invoice_dict[provider_parent_pair_key]
            else:
                invoice = invoice_util.create_invoice(provider.key, parent.key)
                invoice_dict[provider_parent_pair_key] = invoice
            invoice_util.create_invoice_line_item(ndb.Key("Enrollment", enrollment["enrollment_id"]), invoice.key)

    return HttpResponse(status=200)