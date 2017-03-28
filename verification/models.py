from __future__ import unicode_literals

import hashlib
import time
from datetime import datetime
from datetime import timedelta

from google.appengine.ext import ndb
from parent.models import Parent
from login.models import Provider


class VerificationToken(ndb.Model):
    token_id = ndb.StringProperty(required=True)
    _POSSIBLE_TYPES = {'provider_email', 'parent_signup', 'password_reset'}
    type = ndb.StringProperty(required=True)

    provider_key = ndb.KeyProperty(kind=Provider)
    parent_key = ndb.KeyProperty(kind=Parent)

    expiration_date = ndb.DateTimeProperty(required=True)

    @classmethod
    def generate_key(cls, token_id):
        return ndb.Key(cls, token_id)

    @staticmethod
    def create_new_provider_email_token(provider):
        random_str = provider.email + 'provider_email' + str(time.time())
        token_id = hashlib.md5(random_str).hexdigest()
        token = VerificationToken(id=token_id)
        token.token_id = token_id
        token.type = 'provider_email'
        token.provider_key = provider.key
        token.expiration_date = datetime.now() + timedelta(days=60)
        return token

    @staticmethod
    def create_new_provider_password_reset_token(provider):
        random_str = provider.email + 'password_reset' + str(time.time())
        token_id = hashlib.md5(random_str).hexdigest()
        token = VerificationToken(id=token_id)
        token.token_id = token_id
        token.type = 'password_reset'
        token.provider_key = provider.key
        token.expiration_date = datetime.now() + timedelta(days=3)
        return token

    @staticmethod
    def create_new_parent_password_reset_token(parent):
        random_str = parent.email + 'password_reset' + str(time.time())
        token_id = hashlib.md5(random_str).hexdigest()
        token = VerificationToken(id=token_id)
        token.token_id = token_id
        token.type = 'password_reset'
        token.parent_key = parent.key
        token.expiration_date = datetime.now() + timedelta(days=3)
        return token

    @staticmethod
    def create_new_parent_signup_token(parent):
        random_str = parent.email + 'parent_signup' + str(time.time())
        token_id = hashlib.md5(random_str).hexdigest()
        token = VerificationToken(id=token_id)
        token.token_id = token_id
        token.type = 'parent_signup'
        token.parent_key = parent.key
        token.expiration_date = datetime.now() + timedelta(days=3)
        return token
