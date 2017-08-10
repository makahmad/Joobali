"""Package for common dwolla related helper methods and constants"""
import dwollav2
import logging
from os import environ
from tasks.models import DwollaTokens
from google.appengine.api import urlfetch
from datetime import datetime
from common import datetime_util
logger = logging.getLogger(__name__)

# Client constants
CLIENT_ID_PROD = 'XC7mP0GhC2cymZgOvdaHp7IC7FyPBEqex6hU7niubUdbGzEQhX'
CLIENT_SECRET_PROD = 'AVTGFRA4spKTrDPOTFKmlMBKmcjx3RzLlomA8zMiEJnq180fDS'
ENVIRONMENT_PROD = 'production'
CLIENT_ID_UAT = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9'
CLIENT_SECRET_UAT = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9'
ENVIRONMENT_UAT = 'sandbox'


# WEBHOOK SECRET
WEBHOOK_SECRET = 'joobali_webhook_secret_fb2onpb23nbv-9834t-9nv3-4thg49896-34'

UTC_ISO_8601_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
JOOBALI_OUTPUT_FORMAT = '%m/%d/%Y'

client = dwollav2.Client(id=CLIENT_ID_UAT if environ.get('IS_DEV') == 'True' else CLIENT_ID_PROD,
                         secret=CLIENT_SECRET_UAT if environ.get('IS_DEV') == 'True' else CLIENT_SECRET_PROD,
                         environment=ENVIRONMENT_UAT if environ.get('IS_DEV') == 'True' else ENVIRONMENT_PROD)

def create_account_token():
    tokens = DwollaTokens.query().fetch(1)
    if not tokens:
        return # token empty. Page on call!!

    return client.Token(access_token=tokens[0].access_token)

def start_webhook(host_url):
    # Setup webhook to receive transfer status events
    logger.info('Starting webhook: %s' % (host_url + '/tasks/dwollawebhook/'))
    request_body = {
        'url': host_url + '/tasks/dwollawebhook/',
        'secret': 'joobali_webhook_secret_fb2onpb23nb'
    }

    create_account_token().post('webhook-subscriptions', request_body)

def clear_webhook(host):
    webhook_subscriptions = create_account_token().get("webhook-subscriptions").body
    logger.info(webhook_subscriptions)
    # {
    #     u'_links': {
    #         u'self': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'resource-type': u'webhook-subscription',
    #             u'href': u'https://api-sandbox.dwolla.com/webhook-subscriptions'
    #         }
    #     },
    #     u'_embedded': {
    #         u'webhook-subscriptions': [
    #             {
    #                 u'_links': {
    #                     u'self': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'webhook-subscription',
    #                         u'href': u'https://api-sandbox.dwolla.com/webhook-subscriptions/38d21522-5c9c-4b84-86f1-097d5b3bd614'
    #                     },
    #                     u'webhooks': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'webhook',
    #                         u'href': u'https://api-sandbox.dwolla.com/webhook-subscriptions/38d21522-5c9c-4b84-86f1-097d5b3bd614/webhooks'
    #                     }
    #                 },
    #                 u'id': u'38d21522-5c9c-4b84-86f1-097d5b3bd614',
    #                 u'created': u'2017-03-16T05:19:42.000            Z',
    #                 u'url': u'http://joobali-1310.appspot.com/tasks/dwollawebhook',
    #                 u'paused': False
    #             },
    #             {
    #                 u'_links': {
    #                     u'self': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'webhook-subscription',
    #                         u'href': u'https://api-sandbox.dwolla.com/webhook-subscriptions/562a1e16-60a8-4e38-a21d-699260bdba6b'
    #                     },
    #                     u'webhooks': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'webhook',
    #                         u'href': u'https://api-sandbox.dwolla.com/webhook-subscriptions/562a1e16-60a8-4e38-a21d-699260bdba6b/webhooks'
    #                     }
    #                 },
    #                 u'id': u'562a1e16-60a8-4e38-a21d-699260bdba6b',
    #                 u'created': u'2017-05-06T05:57:21.000            Z',
    #                 u'url': u'https://joobali-uat.appspot.com/tasks/dwollawebhook',
    #                 u'paused': False
    #             }
    #         ]
    #     },
    #     u'total': 10
    # }
    for subscription in webhook_subscriptions['_embedded']['webhook-subscriptions']:
        if host in subscription['url']:
            logger.info("Remove webhook: url (%s), id (%s)" % (subscription['url'], subscription['_links']['self']['href']))
            create_account_token().delete(subscription['_links']['self']['href'])

def get_general(url):
    return create_account_token().get(url)

def get_funding_source(funding_source_url):
    # Example Dwolla funding source object
    # {
    #     u'_links': {
    #         u'on-demand-authorization': {
    #             u'resource-type': u'on-demand-authorization',
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-uat.dwolla.com/on-demand-authorizations/cfe74130-2de1-e611-80ee-0aa34a9b2388'
    #         },
    #         u'self': {
    #             u'resource-type': u'funding-source',
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-uat.dwolla.com/funding-sources/593b86cd-7f6a-418e-8fce-61fa7d173b7b'
    #         },
    #         u'balance': {
    #             u'resource-type': u'balance',
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-uat.dwolla.com/funding-sources/593b86cd-7f6a-418e-8fce-61fa7d173b7b/balance'
    #         },
    #         u'customer': {
    #             u'resource-type': u'customer',
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-uat.dwolla.com/customers/45ad438b-dc6f-4210-b9d7-f651a870265b'
    #         }
    #     },
    #     u'name': u'Your Account #1 - CHECKING',
    #     u'status': u'verified',
    #     u'bankName': u'SANDBOX TEST BANK',
    #     u'type': u'bank',
    #     u'id': u'593b86cd-7f6a-418e-8fce-61fa7d173b7b',
    #     u'removed': False,
    #     u'channels': [
    #         u'ach'
    #     ],
    #     u'created': u'2017-01-23T05:31:33.000   Z'
    # }
    logger.info("Get Funding Source: %s" % funding_source_url)
    source = create_account_token().get(funding_source_url).body
    logger.info("Get Funding Source: %s" % source)
    result = {}
    result['name'] = source['name']
    result['bank_name'] = source['bankName'] if 'bankName' in source else ''
    result['status'] = source['status']
    result['type'] = source['type']
    result['removed'] = source['removed']
    result['created_date'] = time_string_from_dwolla_to_joobali(source['created'])
    result['customer_url'] = source['_links']['customer']['href']
    return result

def upload_document(customer_url, document, doc_type):
    urlfetch.set_default_fetch_deadline(60)
    document = create_account_token().post('%s/documents' % customer_url, file=document, documentType=doc_type)
    return document.headers['location']

def get_document(document_url):
    # {
    #     u'_links': {
    #         u'self': {
    #             u'resource-type': u'document',
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-sandbox.dwolla.com/documents/57086708-b440-424e-a80a-021d2ea8b8f8'
    #         }
    #     },
    #     u'id': u'57086708-b440-424e-a80a-021d2ea8b8f8',
    #     u'type': u'idcard',
    #     u'status': u'pending',
    #     u'created': u'2017-06-28T05:48:11.000   Z'
    # }
    document = get_general(document_url).body
    logger.info('Get Document:')
    logger.info(document)
    return document

def list_documents(customer_url):
    # {
    #     u'total': 2,
    #     u'_embedded': {
    #         u'documents': [
    #             {
    #                 u'status': u'pending',
    #                 u'created': u'2017-06-28T05:48:11.000            Z',
    #                 u'type': u'idcard',
    #                 u'id': u'57086708-b440-424e-a80a-021d2ea8b8f8',
    #                 u'_links': {
    #                     u'self': {
    #                         u'href': u'https://api-sandbox.dwolla.com/documents/57086708-b440-424e-a80a-021d2ea8b8f8',
    #                         u'resource-type': u'document',
    #                         u'type': u'application/vnd.dwolla.v1.hal+json'
    #                     }
    #                 }
    #             },
    #             {
    #                 u'status': u'pending',
    #                 u'created': u'2017-06-28T05:47:44.000            Z',
    #                 u'type': u'idcard',
    #                 u'id': u'f6a790ba-85b1-4e54-a055-4b44c97d68aa',
    #                 u'_links': {
    #                     u'self': {
    #                         u'href': u'https://api-sandbox.dwolla.com/documents/f6a790ba-85b1-4e54-a055-4b44c97d68aa',
    #                         u'resource-type': u'document',
    #                         u'type': u'application/vnd.dwolla.v1.hal+json'
    #                     }
    #                 }
    #             }
    #         ]
    #     },
    #     u'_links': {
    #         u'self': {
    #             u'href': u'https://api-sandbox.dwolla.com/customers/dd6a3c07-97bd-4bdb-8079-b2dd3ae809ff/documents',
    #             u'resource-type': u'document',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         }
    #     }
    # }
    documents = create_account_token().get('%s/documents' % customer_url).body
    logger.info("Get Documents:")
    logger.info(documents)
    result = {}
    result['total'] = documents['total']
    result['documents'] = []
    for doc in documents['_embedded']['documents']:
        result['documents'].append({
            'status': doc['status'],
            'type': doc['type'],
            'id': doc['id'],
            'link': doc['_links']['self']['href']
        })
    return result

def make_transfer(request_body):
    logger.info("Making transfer: %s" % request_body)
    return create_account_token().post('transfers', request_body)

def get_micro_deposits(url):
    return create_account_token().get(url)

def verify_micro_deposits(url, first_amount, second_amount):
    logger.info("Verifying Micro Deposits: %s", url)
    request_body = {
        "amount1": {
            "value": str(first_amount),
            "currency": "USD"
        },
        "amount2": {
            "value": str(second_amount),
            "currency": "USD"
        }
    }
    logger.info("Request: %s" % request_body)
    return create_account_token().post('%s/micro-deposits' % url, request_body)

def list_fundings(customer_url):
    return create_account_token().get('%s/funding-sources' % customer_url)

def remove_funding(funding_source_url):
    return create_account_token().post(funding_source_url, {'removed': True})

def get_iav_token(token_url):
    return create_account_token().post(token_url)

def update_customer(customer_id, request_body):
    return create_account_token().post(customer_id, request_body)

def create_customer(request_body):
    return create_account_token().post('customers', request_body)

def list_customers():
    return create_account_token().get('customers')

def get_customer(customer_url):
    # Example Dwolla customer (provider or parents) object
    # {
    #     u'created': u'2016-09-08T22:09:47.980   Z',
    #     u'_links': {
    #         u'edit': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e',
    #             u'resource-type': u'customer'
    #         },
    #         u'transfers': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e/transfers',
    #             u'resource-type': u'transfer'
    #         },
    #         u'send': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-sandbox.dwolla.com/transfers',
    #             u'resource-type': u'transfer'
    #         },
    #         u'receive': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-sandbox.dwolla.com/transfers',
    #             u'resource-type': u'transfer'
    #         },
    #         u'self': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e',
    #             u'resource-type': u'customer'
    #         },
    #         u'edit-form': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json; profile="https://github.com/dwolla/hal-forms"',
    #             u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e',
    #             u'resource-type': u'customer'
    #         },
    #         u'funding-sources': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e/funding-sources',
    #             u'resource-type': u'funding-source'
    #         }
    #     },
    #     u'status': u'verified',
    #     u'id': u'255b92a7-300b-42fc-b72f-5301c0c6c42e',
    #     u'state': u'CA',
    #     u'postalCode': u'94403',
    #     u'email': u'rongjian.lan@gmail.com',
    #     u'city': u'San Mateo',
    #     u'lastName': u'Lan',
    #     u'firstName': u'Rongjian - verified',
    #     u'address1': u'118D 36th Avenue',
    #     u'type': u'personal',
    #     u'phone': u'3015386558'
    # }
    customer = create_account_token().get(customer_url).body
    logger.info('Get Dwolla Customer: %s' % customer)
    result = {}
    result['status'] = customer['status']
    # TODO: need to fetch data ONLY if present
    # result['state'] = customer['state']
    # result['email'] = customer['email']
    # result['city'] = customer['city']
    # result['postal_code'] = customer['postalCode']
    # result['last_name'] = customer['lastName']
    # result['first_name'] = customer['firstName']
    # result['address'] = customer['address1']
    # result['phone'] = customer['phone']
    # result['type'] = customer['type']
    # result['funding_source_url'] = customer['_links']['funding-sources']['href']
    return result


def get_bank_transfer(transfer_url):
    """ Funding transfer is the transfer from bank to dwolla balance.
        See https://discuss.dwolla.com/t/transfer-with-wrong-destination-field/3920 for detail """
    # Example dwolla funding_transfer object
    # {
    #     u'id': u'a777aa33-5b05-e711-80ee-0aa34a9b2388',
    #     u'amount': {
    #         u'currency': u'usd',
    #         u'value': u'500.00'
    #     },
    #     u'_links': {
    #         u'destination': {
    #             u'href': u'https://api-uat.dwolla.com/customers/45ad438b-dc6f-4210-b9d7-f651a870265b',
    #             u'resource-type': u'customer',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'self': {
    #             u'href': u'https://api-uat.dwolla.com/transfers/a777aa33-5b05-e711-80ee-0aa34a9b2388',
    #             u'resource-type': u'transfer',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'failure': {
    #             u'href': u'https://api-uat.dwolla.com/transfers/a777aa33-5b05-e711-80ee-0aa34a9b2388/failure',
    #             u'resource-type': u'failure',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'funded-transfer': {
    #             u'href': u'https://api-uat.dwolla.com/transfers/a877aa33-5b05-e711-80ee-0aa34a9b2388',
    #             u'resource-type': u'transfer',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'source': {
    #             u'href': u'https://api-uat.dwolla.com/funding-sources/593b86cd-7f6a-418e-8fce-61fa7d173b7b',
    #             u'resource-type': u'funding-source',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         }
    #     },
    #     u'clearing': {
    #         u'source': u'standard'
    #     },
    #     u'status': u'failed',
    #     u'created': u'2017-03-10T06:31:33.503   Z'
    # }
    # Another example:
    # {
    #     u'status': u'processed',
    #     u'created': u'2017-07-27T14:16:51.940   Z',
    #     u'clearing': {
    #         u'destination': u'next-day'
    #     },
    #     u'amount': {
    #         u'currency': u'usd',
    #         u'value': u'1.00'
    #     },
    #     u'_links': {
    #         u'source': {
    #             u'resource-type': u'customer',
    #             u'href': u'https://api.dwolla.com/customers/a91a1572-aad4-43b6-9092-a07ad843cede',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'self': {
    #             u'resource-type': u'transfer',
    #             u'href': u'https://api.dwolla.com/transfers/1bf34439-d672-e711-8105-02c4cfdff3c0',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'destination': {
    #             u'resource-type': u'funding-source',
    #             u'href': u'https://api.dwolla.com/funding-sources/e32a7bd4-9f11-4003-a4d2-797f480c0af3',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'funding-transfer': {
    #             u'resource-type': u'transfer',
    #             u'href': u'https://api.dwolla.com/transfers/fad625ed-7c6f-e711-8105-02c4cfdff3c0',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         }
    #     },
    #     u'id': u'1bf34439-d672-e711-8105-02c4cfdff3c0'
    # }
    transfer = create_account_token().get(transfer_url).body
    logger.info(transfer)
    result = {}
    result['amount'] = transfer['amount']['value']
    result['currency'] = transfer['amount']['currency']
    #result['destination_customer_url'] = transfer['_links']['destination']['href']
    #result['failure_url'] = '%s/failure' % transfer['_links']['self']['href']
    result['source_funding_url'] = transfer['_links']['source']['href']
    result['funding_transfer_url'] = transfer['_links']['funding-transfer']['href'] if 'funding-transfer' in transfer['_links'] else None
    result['funded_transfer_url'] = transfer['_links']['funded-transfer']['href'] if 'funded-transfer' in transfer['_links'] else None
    result['status'] = transfer['status']
    result['created_date'] = time_string_from_dwolla_to_joobali(transfer['created'])
    return result

def get_dwolla_transfer(transfer_url):
    """ Funded transfer is the transfer between dwolla balances of two customers.
        The reason it's called "funded" is because the money is already funded from the external bank.
        The transfer from bank to dwolla customer balance is called funding_transfer.
        See https://discuss.dwolla.com/t/transfer-with-wrong-destination-field/3920 for detail """
    # Example dwolla funded_transfer object
    # {
    #     u'status': u'processed',
    #     u'amount': {
    #         u'currency': u'usd',
    #         u'value': u'333.00'
    #     },
    #     u'_links': {
    #         u'self': {
    #             u'resource-type': u'transfer',
    #             u'href': u'https://api-uat.dwolla.com/transfers/48d9977f-c50a-e711-80ef-0aa34a9b2388',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'destination': {
    #             u'resource-type': u'customer',
    #             u'href': u'https://api-uat.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'source': {
    #             u'resource-type': u'customer',
    #             u'href': u'https://api-uat.dwolla.com/customers/45ad438b-dc6f-4210-b9d7-f651a870265b',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'destination-funding-source': {
    #             u'resource-type': u'funding-source',
    #             u'href': u'https://api-uat.dwolla.com/funding-sources/4b683935-4fdf-479e-af0f-13e3911d1799',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'fees':{
    #            u'resource-type': u'fee',
    #            u'href': u'https://api-sandbox.dwolla.com/transfers/d1f0a192-9544-e711-80f2-0aa34a9b2388/fees',
    #            u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'funding-transfer': {
    #             u'resource-type': u'transfer',
    #             u'href': u'https://api-uat.dwolla.com/transfers/47d9977f-c50a-e711-80ef-0aa34a9b2388',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'source-funding-source': {
    #             u'resource-type': u'funding-source',
    #             u'href': u'https://api-uat.dwolla.com/funding-sources/593b86cd-7f6a-418e-8fce-61fa7d173b7b',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         }
    #     },
    #     u'id': u'48d9977f-c50a-e711-80ef-0aa34a9b2388',
    #     u'created': u'2017-03-17T03:55:03.267   Z'
    # }
    # Response in question:
    # {
    #     u'status': u'processed',
    #     u'amount': {
    #         u'currency': u'usd',
    #         u'value': u'73.50'
    #     },
    #     u'_links': {
    #         u'self': {
    #             u'resource-type': u'transfer',
    #             u'href': u'https://api-sandbox.dwolla.com/transfers/71649077-5c49-e711-80f2-0aa34a9b2388',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'destination': {
    #             u'resource-type': u'customer',
    #             u'href': u'https://api-sandbox.dwolla.com/customers/441b7124-12a0-4d76-a9af-48ef513408cc',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'source': {
    #             u'resource-type': u'customer',
    #             u'href': u'https://api-sandbox.dwolla.com/customers/c5313382-e157-4429-b1aa-6dd4564453c6',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'destination-funding-source': {
    #             u'resource-type': u'funding-source',
    #             u'href': u'https://api-sandbox.dwolla.com/funding-sources/e2e57628-11a9-4878-a1f3-fb0e7edc4d5c',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'fees': {
    #             u'resource-type': u'fee',
    #             u'href': u'https://api-sandbox.dwolla.com/transfers/71649077-5c49-e711-80f2-0aa34a9b2388/fees',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         },
    #         u'source-funding-source': {
    #             u'resource-type': u'funding-source',
    #             u'href': u'https://api-sandbox.dwolla.com/funding-sources/96e37ac1-8e14-4a19-8255-1460a1e26c15',
    #             u'type': u'application/vnd.dwolla.v1.hal+json'
    #         }
    #     },
    #     u'id': u'71649077-5c49-e711-80f2-0aa34a9b2388',
    #     u'created': u'2017-06-04T19:31:55.917   Z'
    # }
    transfer = create_account_token().get(transfer_url).body
    logger.info(transfer)
    result = {}
    result['amount'] = transfer['amount']['value']
    result['currency'] = transfer['amount']['currency']
    result['source_funding_url'] = transfer['_links']['source-funding-source']['href']
    result['destination_funding_url'] = transfer['_links']['destination-funding-source']['href']
    result['source_customer_url'] = transfer['_links']['source']['href']
    result['destination_customer_url'] = transfer['_links']['destination']['href']
    result['funding_transfer_url'] = transfer['_links']['funding-transfer']['href'] if 'funding-transfer' in transfer['_links'] else None
    result['fee_transfer_url'] = transfer['_links']['fees']['href'] if 'fees' in transfer['_links'] else None
    result['status'] = transfer['status']
    result['created_date'] = time_string_from_dwolla_to_joobali(transfer['created'])
    if 'cancel' in transfer['_links']:
        result['cancel'] = transfer['_links']['cancel']['href']
    return result

def cancel_transfer(cancel_url):
    logger.info('Cancelling transfer: %s' % cancel_url);
    request_body = {
        'status': 'cancelled',
    }
    create_account_token().post(cancel_url, request_body)

def get_fee_transfer(fee_transfer_url):
    """ Fee transfer is the transfer incurred from charging fees for normal dwolla transfer. """
    # {
    #     u'_links': {
    #         u'self': {
    #             u'type': u'application/vnd.dwolla.v1.hal+json',
    #             u'resource-type': u'fee',
    #             u'href': u'https://api-sandbox.dwolla.com/transfers/d1f0a192-9544-e711-80f2-0aa34a9b2388/fees'
    #         }
    #     },
    #     u'total': 1,
    #     u'_embedded': {
    #         u'fees': [
    #             {
    #                 u'_links': {
    #                     u'created-from-transfer': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'transfer',
    #                         u'href': u'https://api-sandbox.dwolla.com/transfers/d1f0a192-9544-e711-80f2-0aa34a9b2388'
    #                     },
    #                     u'self': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'transfer',
    #                         u'href': u'https://api-sandbox.dwolla.com/transfers/811bf85d-5f52-4855-b1cf-54413e309a22'
    #                     },
    #                     u'source': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'customer',
    #                         u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'
    #                     },
    #                     u'destination': {
    #                         u'type': u'application/vnd.dwolla.v1.hal+json',
    #                         u'resource-type': u'account',
    #                         u'href': u'https://api-sandbox.dwolla.com/accounts/aaa5e130-ce8d-4807-82db-90961f7f1240'
    #                     }
    #                 },
    #                 u'id': u'811bf85d-5f52-4855-b1cf-54413e309a22',
    #                 u'amount': {
    #                     u'value': u'5.99',
    #                     u'currency': u'usd'
    #                 },
    #                 u'status': u'pending',
    #                 u'created': u'2017-05-29T17:38:06.873            Z'
    #             }
    #         ]
    #     },
    #     u'transactions': [
    #         {
    #             u'_links': {
    #                 u'created-from-transfer': {
    #                     u'type': u'application/vnd.dwolla.v1.hal+json',
    #                     u'resource-type': u'transfer',
    #                     u'href': u'https://api-sandbox.dwolla.com/transfers/d1f0a192-9544-e711-80f2-0aa34a9b2388'
    #                 },
    #                 u'self': {
    #                     u'type': u'application/vnd.dwolla.v1.hal+json',
    #                     u'resource-type': u'transfer',
    #                     u'href': u'https://api-sandbox.dwolla.com/transfers/811bf85d-5f52-4855-b1cf-54413e309a22'
    #                 },
    #                 u'source': {
    #                     u'type': u'application/vnd.dwolla.v1.hal+json',
    #                     u'resource-type': u'customer',
    #                     u'href': u'https://api-sandbox.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'
    #                 },
    #                 u'destination': {
    #                     u'type': u'application/vnd.dwolla.v1.hal+json',
    #                     u'resource-type': u'account',
    #                     u'href': u'https://api-sandbox.dwolla.com/accounts/aaa5e130-ce8d-4807-82db-90961f7f1240'
    #                 }
    #             },
    #             u'id': u'811bf85d-5f52-4855-b1cf-54413e309a22',
    #             u'amount': {
    #                 u'value': u'5.99',
    #                 u'currency': u'usd'
    #             },
    #             u'status': u'pending',
    #             u'created': u'2017-05-29T17:38:06.873         Z'
    #         }
    #     ]
    # }
    fee_transfer = create_account_token().get(fee_transfer_url).body
    logger.info(fee_transfer)
    result = {}
    if fee_transfer['total'] > 1:
        logger.warning('More than one fee transfer exists for transfer: %s' % fee_transfer_url)
    result['amount'] = fee_transfer['_embedded']['fees'][0]['amount']['value']
    result['currency'] = fee_transfer['_embedded']['fees'][0]['amount']['currency']
    result['status'] = fee_transfer['_embedded']['fees'][0]['status']
    result['created_date'] = time_string_from_dwolla_to_joobali(fee_transfer['_embedded']['fees'][0]['created'])
    return result

def parse_webhook_data(webhook_json):
    # Example webhook event json:
    # Bank Transfer events (transfer id = fad625ed-7c6f-e711-8105-02c4cfdff3c0)
    # No.1 - customer is the sender
    # {
    #     u'created': u'2017-07-23T08:00:05.074   Z',
    #     u'resourceId': u'fad625ed-7c6f-e711-8105-02c4cfdff3c0',
    #     u'topic': u'customer_transfer_created',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api.dwolla.com/customers/f6b8af24-f1a1-48ee-a211-547f78bdfee6'
    #         },
    #         u'self': {
    #             u'href': u'https://api.dwolla.com/events/775f875c-1b82-45ff-b4e8-f9fea23ac5ef'
    #         },
    #         u'resource': {
    #             u'href': u'https://api.dwolla.com/transfers/fad625ed-7c6f-e711-8105-02c4cfdff3c0'
    #         },
    #         u'account': {
    #             u'href': u'https://api.dwolla.com/accounts/6d081097-35f7-4119-9c4e-530d35de2711'
    #         }
    #     },
    #     u'timestamp': u'2017-07-23T08:00:05.074   Z',
    #     u'id': u'775f875c-1b82-45ff-b4e8-f9fea23ac5ef'
    # }
    #
    # No.2 - customer is the receiver
    # {
    #     u'created': u'2017-07-23T08:00:04.993   Z',
    #     u'resourceId': u'fad625ed-7c6f-e711-8105-02c4cfdff3c0',
    #     u'topic': u'customer_transfer_created',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api.dwolla.com/customers/a91a1572-aad4-43b6-9092-a07ad843cede'
    #         },
    #         u'self': {
    #             u'href': u'https://api.dwolla.com/events/3e7a2266-832b-4325-9207-2ff3c2eabe3e'
    #         },
    #         u'resource': {
    #             u'href': u'https://api.dwolla.com/transfers/fad625ed-7c6f-e711-8105-02c4cfdff3c0'
    #         },
    #         u'account': {
    #             u'href': u'https://api.dwolla.com/accounts/6d081097-35f7-4119-9c4e-530d35de2711'
    #         }
    #     },
    #     u'timestamp': u'2017-07-23T08:00:04.993   Z',
    #     u'id': u'3e7a2266-832b-4325-9207-2ff3c2eabe3e'
    # }
    # No.3 - customer is the sender
    # {
    #     u'created': u'2017-07-27T14:13:31.921   Z',
    #     u'resourceId': u'fad625ed-7c6f-e711-8105-02c4cfdff3c0',
    #     u'topic': u'customer_transfer_completed',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api.dwolla.com/customers/f6b8af24-f1a1-48ee-a211-547f78bdfee6'
    #         },
    #         u'self': {
    #             u'href': u'https://api.dwolla.com/events/20892257-9826-4173-9a7a-671960a25c70'
    #         },
    #         u'resource': {
    #             u'href': u'https://api.dwolla.com/transfers/fad625ed-7c6f-e711-8105-02c4cfdff3c0'
    #         },
    #         u'account': {
    #             u'href': u'https://api.dwolla.com/accounts/6d081097-35f7-4119-9c4e-530d35de2711'
    #         }
    #     },
    #     u'timestamp': u'2017-07-27T14:13:31.921   Z',
    #     u'id': u'20892257-9826-4173-9a7a-671960a25c70'
    # }
    # No.4 - customer is the receiver
    # {
    #     u'created': u'2017-07-27T14:13:31.877   Z',
    #     u'resourceId': u'fad625ed-7c6f-e711-8105-02c4cfdff3c0',
    #     u'topic': u'customer_transfer_completed',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api.dwolla.com/customers/a91a1572-aad4-43b6-9092-a07ad843cede'
    #         },
    #         u'self': {
    #             u'href': u'https://api.dwolla.com/events/0c507e1b-71e8-4c52-82f4-1ed443dea5d8'
    #         },
    #         u'resource': {
    #             u'href': u'https://api.dwolla.com/transfers/fad625ed-7c6f-e711-8105-02c4cfdff3c0'
    #         },
    #         u'account': {
    #             u'href': u'https://api.dwolla.com/accounts/6d081097-35f7-4119-9c4e-530d35de2711'
    #         }
    #     },
    #     u'timestamp': u'2017-07-27T14:13:31.877   Z',
    #     u'id': u'0c507e1b-71e8-4c52-82f4-1ed443dea5d8'
    # }
    # No.5 - customer is the receiver
    # {
    #     u'created': u'2017-07-27T14:16:32.625   Z',
    #     u'resourceId': u'aa391733-d672-e711-8105-02c4cfdff3c0',
    #     u'topic': u'customer_bank_transfer_created',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api.dwolla.com/customers/a91a1572-aad4-43b6-9092-a07ad843cede'
    #         },
    #         u'self': {
    #             u'href': u'https://api.dwolla.com/events/69ee9ca2-53b9-4fd8-bb9e-dbfd8d4f46a8'
    #         },
    #         u'resource': {
    #             u'href': u'https://api.dwolla.com/transfers/aa391733-d672-e711-8105-02c4cfdff3c0'
    #         },
    #         u'account': {
    #             u'href': u'https://api.dwolla.com/accounts/6d081097-35f7-4119-9c4e-530d35de2711'
    #         }
    #     },
    #     u'timestamp': u'2017-07-27T14:16:32.625   Z',
    #     u'id': u'69ee9ca2-53b9-4fd8-bb9e-dbfd8d4f46a8'
    # }
    # No.6 - customer is the receiver
    # {
    #     u'created': u'2017-07-28T14:02:11.214   Z',
    #     u'resourceId': u'aa391733-d672-e711-8105-02c4cfdff3c0',
    #     u'topic': u'customer_bank_transfer_completed',
    #     u'_links': {
    #         u'customer': {
    #             u'href': u'https://api.dwolla.com/customers/a91a1572-aad4-43b6-9092-a07ad843cede'
    #         },
    #         u'self': {
    #             u'href': u'https://api.dwolla.com/events/637e03db-c474-4d60-9975-617edb0aaa35'
    #         },
    #         u'resource': {
    #             u'href': u'https://api.dwolla.com/transfers/aa391733-d672-e711-8105-02c4cfdff3c0'
    #         },
    #         u'account': {
    #             u'href': u'https://api.dwolla.com/accounts/6d081097-35f7-4119-9c4e-530d35de2711'
    #         }
    #     },
    #     u'timestamp': u'2017-07-28T14:02:11.214   Z',
    #     u'id': u'637e03db-c474-4d60-9975-617edb0aaa35'
    # }
    #
    # Funding source removal event:
    # {u'created': u'2017-03-26T23:12:47.553Z', u'resourceId': u'a3f37a8e-8e8e-4ffe-9025-0d25df7f469e',
    #  u'topic': u'customer_funding_source_removed',
    #  u'_links': {u'customer': {u'href': u'https://api-uat.dwolla.com/customers/255b92a7-300b-42fc-b72f-5301c0c6c42e'},
    #              u'self': {u'href': u'https://api-uat.dwolla.com/events/f6071cba-6fc5-4b4e-86b1-68cb7ba509ff'},
    #              u'resource': {
    #                  u'href': u'https://api-uat.dwolla.com/funding-sources/a3f37a8e-8e8e-4ffe-9025-0d25df7f469e'},
    #              u'account': {u'href': u'https://api-uat.dwolla.com/accounts/aaa5e130-ce8d-4807-82db-90961f7f1240'}},
    #  u'timestamp': u'2017-03-26T23:12:47.553Z', u'id': u'f6071cba-6fc5-4b4e-86b1-68cb7ba509ff'}

    result = {}
    result['id'] = webhook_json['id']
    result['topic'] = webhook_json['topic']
    result['customer_url'] = webhook_json['_links']['customer']['href']
    result['event_url'] = webhook_json['_links']['self']['href']
    result['resource_url'] = webhook_json['_links']['resource']['href']
    result['account_url'] = webhook_json['_links']['account']['href']
    result['event_date'] = time_string_from_dwolla_to_joobali(webhook_json['timestamp'])
    return result


def time_string_from_dwolla_to_joobali(dwolla_timestamp):
    ''' Parse dwolla UTC timestamp, convert to PST, and output in joobali time format. '''
    timestamp = datetime.strptime(dwolla_timestamp, UTC_ISO_8601_TIME_FORMAT)
    return datetime_util.utc_to_local(timestamp).strftime(JOOBALI_OUTPUT_FORMAT)