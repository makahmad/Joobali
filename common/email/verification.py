import logging
from google.appengine.api import mail
from django.template import Context, loader
from os import environ

logger = logging.getLogger(__name__)
_provider_email_verification_template = loader.get_template('verification/provider_email_verification.html')


def send_provider_email_address_verification(verification_token, host, sender_address='howdy@joobali.com'):
    # [START send_mail]
    provider = verification_token.provider_key.get()
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Joobali: Please verify your email address")

    message.to = "%s" % provider.email
    http_prefix = 'http://' if environ.get('IS_DEV') else 'https://'
    verification_link = http_prefix + host + '/verification/provideremail?t=' + verification_token.token_id
    data = {
        'provider_school_name': provider.schoolName,
        'verification_link': verification_link
    }
    message.html = _provider_email_verification_template.render(Context(data))
    message.send()

    # [END send_mail]
