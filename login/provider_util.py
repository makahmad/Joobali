from models import Provider, ProviderIdCounter
from google.appengine.ext import ndb
import base64
import random

def get_provider_by_email(email):
    qry = Provider.query(Provider.email == email)
    for parent in qry.fetch():
        return parent
