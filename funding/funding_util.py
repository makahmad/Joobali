
from common.dwolla import create_account_token
from invoice.models import Invoice
import dwollav2
import logging

logger = logging.getLogger(__name__)
account_token = create_account_token('sandbox')

def make_transfer(dest_customer_url, funding_source, amount, invoice=None):
    """Make Dwolla Money Transfer"""
    fundings_url = '%s/funding-sources' % dest_customer_url
    logger.info(fundings_url)
    funding_sources = account_token.get(fundings_url)
    dest_funding_source_id = None # TODO(rongjian): allow users to set receiving bank source.
    for funding in funding_sources.body['_embedded']['funding-sources']:
        dest_funding_source_id = funding['id']
    request_body = {
        '_links': {
            'destination': {
                'href': 'https://api.dwolla.com/funding-sources/' + dest_funding_source_id
            },
            'source': {
                'href': 'https://api.dwolla.com/funding-sources/' + funding_source
            }
        },
        'amount': {
            'currency': 'USD',
            'value': amount
        },
        'fees': [
            {
                '_links': {
                    'charge-to':{
                        'href': dest_customer_url
                    }
                },
                'amount': {
                    'value': round(amount * 0.01, 2),
                    'currency': 'USD'
                }
            }
        ]
    }
    transfer = account_token.post('transfers', request_body)
    if invoice:
        invoice.dwolla_transfer_id = transfer.headers['location'] # funded_transfer url
        invoice.status = Invoice._POSSIBLE_STATUS['PROCESSING']
        invoice.put()

def list_fundings(customer_url):
    fundings = []
    funding_sources = account_token.get('%s/funding-sources' % customer_url)
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
            fundings.append({
                "status": funding['status'],
                "type": funding['type'],
                "name": funding['name'],
                "id": funding['id'],
                "url": funding['_links']['self']['href'],
            })
    return fundings