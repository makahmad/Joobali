
from common import dwolla
from invoice.models import Invoice
from login.models import Provider
from login import provider_util
import logging
from os import environ
from funding.models import FeeRate
from parent import parent_util
from payments import payments_util
from datetime import datetime
from common import datetime_util

logger = logging.getLogger(__name__)

DATE_FORMAT = '%m/%d/%Y'

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

    fee = 0
    if rate and rate <= 0.1: # 0.1 is a sane upper limit
        fee = round(amount * rate, 2)
        request_body['fees'] =  [
            {
                '_links': {
                    'charge-to':{
                        'href': dest_customer_url
                    }
                },
                'amount': {
                    'value': fee,
                    'currency': 'USD'
                }
            }
        ]

    transfer_response = dwolla.make_transfer(request_body)

    if invoice:
        invoice.dwolla_transfer_id = transfer_response.headers['location'] # dwolla_transfer url
        invoice.is_payment_cancellable = True
        invoice.status = Invoice._POSSIBLE_STATUS['PROCESSING']
        invoice.put()

        if transfer_response and transfer_response.headers['location']:
            transfer = dwolla.get_dwolla_transfer(transfer_response.headers['location'])
            amount = float(transfer['amount'])
            # source_customer_url = transfer['source_customer_url']
            status = transfer['status']
            date = transfer['created_date']
            provider = invoice.provider_key.get()
            parent = parent_util.get_parents_by_email(invoice.parent_email)
            payment_type = 'Online Transfer'
            fee_amount = fee

            if parent:
                payment_date = datetime_util.local_to_utc(datetime.strptime(date, DATE_FORMAT))
                payments_util.add_payment_maybe_for_invoice(provider, invoice.child_key.get(), amount, parent.full_name(), payment_date, payment_type,
                                                            None, invoice, status, fee_amount, transfer_response.headers['location'])

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

        # Example funding for micro-deposit:
        # {
        #     u'id': u'fa7f4d01-df87-4256-bd41-30c20a7f38ac',
        #     u'status': u'unverified',
        #     u'created': u'2017-08-05T04:50:51.000      Z',
        #     u'_links': {
        #         # 'initiate-micro-deposits' if micro-deposit is not started.
        #         u'micro-deposits': {
        #             u'type': u'application/vnd.dwolla.v1.hal+json',
        #             u'href': u'https://api-sandbox.dwolla.com/funding-sources/fa7f4d01-df87-4256-bd41-30c20a7f38ac/micro-deposits',
        #             u'resource-type': u'micro-deposits'
        #         },
        #         u'on-demand-authorization': {
        #             u'type': u'application/vnd.dwolla.v1.hal+json',
        #             u'href': u'https://api-sandbox.dwolla.com/on-demand-authorizations/959b60d0-9979-e711-80f4-0aa34a9b2388',
        #             u'resource-type': u'on-demand-authorization'
        #         },
        #         u'self': {
        #             u'type': u'application/vnd.dwolla.v1.hal+json',
        #             u'href': u'https://api-sandbox.dwolla.com/funding-sources/fa7f4d01-df87-4256-bd41-30c20a7f38ac',
        #             u'resource-type': u'funding-source'
        #         },
        #         u'verify-micro-deposits': {
        #             u'type': u'application/vnd.dwolla.v1.hal+json',
        #             u'href': u'https://api-sandbox.dwolla.com/funding-sources/fa7f4d01-df87-4256-bd41-30c20a7f38ac/micro-deposits',
        #             u'resource-type': u'micro-deposits'
        #         },
        #         u'customer': {
        #             u'type': u'application/vnd.dwolla.v1.hal+json',
        #             u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e',
        #             u'resource-type': u'customer'
        #         }
        #     },
        #     u'name': u'026009593',
        #     u'bankName': u'SANDBOX TEST BANK',
        #     u'type': u'bank',
        #     u'removed': False,
        #     u'channels': [
        #         u'ach'
        #     ]
        # }
        if funding['type'] != 'balance' and funding['removed'] != True:
            if funding['status'] == 'verified':
                funding['status'] = 'Connected'
            elif funding['status'] == 'unverified':
                if 'initiate-micro-deposits' in funding['_links']:
                    funding['status'] = 'Pending micro-deposit initiation'
                elif 'verify-micro-deposits' in funding['_links']:
                    funding['status'] = 'Pending micro-deposit verification'
                elif 'micro-deposits' in funding['_links']:
                    funding['status'] = 'Micro-deposit in progress'
            if funding['type'] == 'bank':
                funding['type'] = 'Bank'

            fundings.append({
                "status": funding['status'],
                "type": funding['type'],
                "name": funding['name'],
                "id": funding['id'],
                "url": funding['_links']['self']['href'],
                'initiate-micro-deposits': funding['_links']['initiate-micro-deposits']['href'] if 'initiate-micro-deposits' in funding['_links'] else None,
                'micro-deposits': funding['_links']['micro-deposits']['href'] if 'micro-deposits' in funding['_links'] else None,
                'verify-micro-deposits': funding['_links']['verify-micro-deposits']['href'] if 'verify-micro-deposits' in funding['_links'] else None,
            })
    return fundings


def get_fee_rate(provider_id):
    provider_key = Provider.generate_key(provider_id)
    rate_query = FeeRate.query(FeeRate.provider_key == provider_key)
    for rate in rate_query:
        return rate.rate
    return None