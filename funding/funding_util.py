
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
        }
    }
    transfer = account_token.post('transfers', request_body)
    if invoice:
        invoice.dwolla_transfer_id = transfer.headers['location'] # funded_transfer url
        invoice.status = Invoice._POSSIBLE_STATUS['PROCESSING']
        invoice.put()

def list_fundings(customer_url):
    fundings = []
    funding_sources = account_token.get('%s/funding-sources' % customer_url)
    for funding in funding_sources.body['_embedded']['funding-sources']:
        if funding['type'] != 'balance':
            fundings.append({
                "status": funding['status'],
                "type": funding['type'],
                "name": funding['name'],
                "id": funding['id']
            })
    return fundings