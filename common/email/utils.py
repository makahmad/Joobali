from os import environ
from google.appengine.api import mail
import logging

logger = logging.getLogger(__name__)


def send_email(sender, to, subject, html_content, body):
    """
        Wrapper method that wrap the email sending process.
    :param sender: the sender address
    :param to: the receiver email address
    :param subject: the subject of the email
    :param html_content: the html content of the email
    :param body: if the html_content is not set, this body will be used for the content of the email
    :return: True if the mail was send successfully, False if not.
    """

    # Overrides the sender and receiver if the server is running in dev
    if environ["IS_DEV"] and 'OVERRIDING_EMAIL' in environ and len(environ['OVERRIDING_EMAIL']) != 0:
        sender = environ["OVERRIDING_EMAIL"]
        to = environ["OVERRIDING_EMAIL"]

    message = mail.EmailMessage(
        sender=sender,
        to=to,
        subject=subject)
    if html_content:
        message.html = html_content
    if body:
        message.body = body
    message.send()
