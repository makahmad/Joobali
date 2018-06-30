import logging
from django.http import HttpResponse
from dwollav2.error import ValidationError
from common.dwolla import  get_customer


logger = logging.getLogger(__name__)


def get_dwolla_status(provider):
    """Returns the dwolla status"""
    if provider is not None:
        if provider.dwolla_status is None or provider.dwolla_status != 'verified':
            try:
                dwolla_customer = get_customer(provider.customerId)
                if dwolla_customer:
                    provider.dwolla_status = dwolla_customer['status']
                    provider.put()
            except ValidationError:
                provider.dwolla_status = None
        return provider.dwolla_status
    return 'Unknown'
