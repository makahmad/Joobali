from django.template import Context, loader
from os import environ
from common.email.utils import send_email

_forget_password_email_template = loader.get_template('login/forgot_password_email.html')
_provider_email_verification_template = loader.get_template('verification/provider_email_verification.html')


def send_reset_password_email_for_provider(token, host, sender_address="Joobali <howdy@joobali.com>"):
    _send_reset_password_email(token, host, sender_address, 'provider')


def send_reset_password_email_for_parent(token, host, sender_address="Joobali <howdy@joobali.com>"):
    _send_reset_password_email(token, host, sender_address, 'parent')


def _send_reset_password_email(token, host, sender_address="Joobali <howdy@joobali.com>", user_type='provider'):
    if user_type == 'provider':
        provider = token.provider_key.get()
        receiver_address = provider.email
        receiver_name = provider.firstName
    elif user_type == 'parent':
        parent = token.parent_key.get()
        receiver_address = parent.email
        receiver_name = parent.first_name
    http_prefix = 'http://' if environ.get('IS_DEV') == 'True' else 'https://'
    root_path = http_prefix + host
    reset_password_link = root_path + "/login/reset?t=" + token.token_id

    email_subject = "Joobali password reset for %s" % receiver_address
    email_to = "%s <%s>" % (receiver_name, receiver_address)

    data = {
        'root_path': root_path,
        'reset_password_link': reset_password_link,
        'first_name': receiver_name,
        'host': http_prefix + host,
    }
    email_html_content = _forget_password_email_template.render(data)

    send_email(sender=sender_address, subject=email_subject, to=email_to, html_content=email_html_content)


def send_provider_email_address_verification(verification_token, host, sender_address='Joobali <howdy@joobali.com>'):
    provider = verification_token.provider_key.get()

    email_subject = "Joobali: Please confirm your email address"
    email_to = "%s" % provider.email
    http_prefix = 'http://' if environ.get('IS_DEV') == 'True' else 'https://'
    verification_link = http_prefix + host + '/verification/provideremail?t=' + verification_token.token_id
    data = {
        'provider_school_name': provider.schoolName,
        'verification_link': verification_link,
        'host': http_prefix + host,
    }
    email_html_content = _provider_email_verification_template.render(data)

    send_email(sender=sender_address, subject=email_subject, to=email_to, html_content=email_html_content)
