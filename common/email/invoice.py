import logging

from google.appengine.api import mail

logger = logging.getLogger(__name__)


def send_invoice_email(parent_address, invoice, start_date, end_date, template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Reminder: You have an invoice due.")

    message.to = "%s" % parent_address
    message.body = """Joobali Reminder Child Care Payment Due

Payment Due Date: 	%s
Billing Period: 		%s - %s

Our records indicate you are signed up for Joobali AutoPay. Joobali AutoPay will process this payment on the due date indicated
""" % (invoice.due_date, start_date, end_date)

    message.html = template
    message.send()

    # [END send_mail]

