from models import Provider, ProviderIdCounter
from google.appengine.ext import ndb
import base64
import random

def get_provider_by_email(email):
    qry = Provider.query(Provider.email == email)
    for parent in qry.fetch():
        return parent

def get_provider_by_dwolla_id(customer_url):
    result = Provider.query(Provider.customerId == customer_url).fetch(1)
    if result:
        return result[0]
    return None