from django.template import Context, loader
from common.email.utils import send_email

_autopay_scheduled_email_template = loader.get_template('funding/joobali-to-customer-autopay-scheduled.html')
_autopay_cancelled_email_template = loader.get_template('funding/joobali-to-customer-autopay-cancelled.html')


def send_autopay_scheduled_email(receiver_name, receiver_address, data, sender_address="Joobali <howdy@joobali.com>"):
    email_subject="Autopay Scheduled!"
    email_to = "%s <%s>" % (receiver_name, receiver_address)
    email_html = _autopay_scheduled_email_template.render(data)

    send_email(sender=sender_address, subject=email_subject, to=email_to, html_content=email_html)


def send_autopay_cancelled_email(receiver_name, receiver_address, data, sender_address="Joobali <howdy@joobali.com>"):
    email_subject="Autopay Cancelled!"
    email_to = "%s <%s>" % (receiver_name, receiver_address)
    email_html = _autopay_cancelled_email_template.render(data)

    send_email(sender=sender_address, subject=email_subject, to=email_to, html_content=email_html)
