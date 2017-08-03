
from common import dwolla
from invoice.models import Invoice
from login.models import Provider
import logging
from os import environ
from funding.models import FeeRate

logger = logging.getLogger(__name__)

def make_transfer(dest_customer_url, funding_source, amount, invoice=None, rate=None):
    """Make Dwolla Money Transfer"""
    funding_sources = dwolla.list_fundings(dest_customer_url)
    dest_funding_source_id = None # TODO(rongjian): allow users to set receiving bank source.
    for funding in funding_sources.body['_embedded']['funding-sources']:
        logger.info(funding)
        if funding['name'] != 'Balance' and funding['removed'] is False:
            dest_funding_source_id = funding['id']
            break
    request_body = {
        '_links': {
            'destination': {
                'href': 'https://%s.dwolla.com/funding-sources/%s' % ('api-sandbox' if environ.get('IS_DEV') == 'True' else 'api', dest_funding_source_id)
            },
            'source': {
                'href': 'https://%s.dwolla.com/funding-sources/%s' % ('api-sandbox' if environ.get('IS_DEV') == 'True' else 'api', funding_source)
            }
        },
        'amount': {
            'currency': 'USD',
            'value': amount
        }
    }

    if rate and rate <= 0.1: # 0.1 is a sane upper limit
        request_body['fees'] =  [
            {
                '_links': {
                    'charge-to':{
                        'href': dest_customer_url
                    }
                },
                'amount': {
                    'value': round(amount * rate, 2),
                    'currency': 'USD'
                }
            }
        ]

    transfer = dwolla.make_transfer(request_body)

    if invoice:
        invoice.dwolla_transfer_id = transfer.headers['location'] # funded_transfer url
        invoice.status = Invoice._POSSIBLE_STATUS['PROCESSING']
        invoice.put()

def list_fundings(customer_url):
    fundings = []
    funding_sources = dwolla.list_fundings(customer_url)
    logger.info("Funding sources: %s" % funding_sources.body['_embedded']['funding-sources'])
    for funding in funding_sources.body['_embedded']['funding-sources']:
        # Example funding:
        # {u'id': u'31245d2d-7ac4-46c5-8b97-731be8ce7bd2', u'channels': [u'ach'], u'created': u'2016-10-12T23:26:11.000Z',
        #  u'_links': {u'initiate-micro-deposits': {u'type': u'application/vnd.dwolla.v1.hal+json',
        #                                           u'resource-type': u'micro-deposits',
        #                                           u'href': u'https://api-uat.dwolla.com/funding-sources/31245d2d-7ac4-46c5-8b97-731be8ce7bd2/micro-deposits'},
        #              u'self': {u'type': u'application/vnd.dwolla.v1.hal+json', u'resource-type': u'funding-source',
        #                        u'href': u'https://api-uat.dwolla.com/funding-sources/31245d2d-7ac4-46c5-8b97-731be8ce7bd2'},
        #              u'customer': {u'type': u'application/vnd.dwolla.v1.hal+json', u'resource-type': u'customer',
        #                            u'href': u'https://api-uat.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'}},
        #  u'status': u'unverified', u'type': u'bank', u'name': u'123', u'removed': True}
        if funding['type'] != 'balance' and funding['removed'] != True:
            if funding['status'] == 'verified':
                funding['status'] = 'Connected'

            if funding['type'] == 'bank':
                funding['type'] = 'Bank'

            fundings.append({
                "status": funding['status'],
                "type": funding['type'],
                "name": funding['name'],
                "id": funding['id'],
                "url": funding['_links']['self']['href'],
            })
    return fundings


def get_fee_rate(provider_id):
    provider_key = Provider.generate_key(provider_id)
    rate_query = FeeRate.query(FeeRate.provider_key == provider_key)
    for rate in rate_query:
        return rate.rate
    return None