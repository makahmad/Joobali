import logging

from google.appengine.api import mail

from common.email.utils import send_email

logger = logging.getLogger(__name__)


def send_invoice_email(parent_address, invoice, start_date, end_date, template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    email_body = """Joobali Reminder Child Care Payment Due

Payment Due Date: 	%s
Billing Period: 		%s - %s

Our records indicate you are signed up for Joobali AutoPay. Joobali AutoPay will process this payment on the due date indicated
""" % (invoice.due_date, start_date, end_date)
    email_subject = "Reminder: You have an invoice due."
    email_to = "%s" % parent_address
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=template, body=email_body)

    # [END send_mail]

