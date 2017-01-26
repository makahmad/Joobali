
from common.dwolla import create_account_token
import dwollav2
import logging

logger = logging.getLogger(__name__)
account_token = create_account_token('sandbox')

def make_transfer(dest_customer_id, funding_source, amount):
    """Make Dwolla Money Transfer"""
    request_body = {
        '_links': {
            'destination': {
                'href': 'https://api.dwolla.com/customers/' + dest_customer_id
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
    account_token.post('transfers', request_body)

