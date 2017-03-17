import os
import logging
from google.appengine.api import mail
from django.template import loader
from django.template import Context

logger = logging.getLogger(__name__)

def send_payment_success_email(parent_address, parent_name, school_name, amount, sender_address="rongjian@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Reminder: You have successfully paid.")

    message.to = "%s" % parent_address
    message.body = """Hi, %s
    You've successfully paid <%s> $%s.""" % (parent_name, school_name, amount)

    message.send()



def send_payment_failure_email(parent_address, parent_name, school_name, amount, sender_address="rongjian@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Reminder: You have successfully paid.")

    message.to = "%s" % parent_address
    message.body = """Hi, %s
    Your payment of $%s to <%s> was denied by the bank. Please try again.""" % (parent_name, school_name, amount)

    message.send()
