from google.appengine.api import mail
from django.template import Context, loader
from os import environ

_autopay_scheduled_email_template = loader.get_template('funding/joobali-to-customer-autopay-scheduled.html')
_autopay_cancelled_email_template = loader.get_template('funding/joobali-to-customer-autopay-cancelled.html')


def send_autopay_scheduled_email(receiver_name, receiver_address, data, sender_address="Joobali <howdy@joobali.com>"):
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Autopay Scheduled!")

    message.to = "%s <%s>" % (receiver_name, receiver_address)
    message.html = _autopay_scheduled_email_template.render(Context(data))
    message.send()


def send_autopay_cancelled_email(receiver_name, receiver_address, data, sender_address="Joobali <howdy@joobali.com>"):
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Autopay Cancelled!")

    message.to = "%s <%s>" % (receiver_name, receiver_address)
    message.html = _autopay_cancelled_email_template.render(Context(data))
    message.send()

    # [END send_mail]