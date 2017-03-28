from google.appengine.api import mail
from django.template import loader
from os import environ

_forget_password_email_template = loader.get_template('login/forgot_password_email.html')


def send_reset_password_email_for_provider(token, host, sender_address="howdy@joobali.com"):
    _send_reset_password_email(token, host, sender_address, 'provider')


def send_reset_password_email_for_parent(token, host, sender_address="howdy@joobali.com"):
    _send_reset_password_email(token, host, sender_address, 'parent')


def _send_reset_password_email(token, host, sender_address="howdy@joobali.com", user_type='provider'):
    if user_type == 'provider':
        provider = token.provider_key.get()
        receiver_address = provider.email
        receiver_name = provider.firstName
    elif user_type == 'parent':
        parent = token.parent_key.get()
        receiver_address = parent.email
        receiver_name = parent.first_name
    http_prefix = 'http://' if environ.get('IS_DEV') else 'https://'
    root_path = http_prefix + host
    reset_password_link = root_path + "/login/reset?t=" + token.token_id
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Joobali password reset for %s" % receiver_address)

    message.to = "%s <%s>" % (receiver_name, receiver_address)
    data = {
        'root_path': root_path,
        'reset_password_link': reset_password_link
    }
    message.html = _forget_password_email_template.render(data)
    message.send()
