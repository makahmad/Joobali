import logging
from google.appengine.api import mail

logger = logging.getLogger(__name__)

def send_payment_processing_email(parent_address, parent_name, school_name, amount, sender_address="rongjian@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Your payment to %s is being processed." % school_name)

    message.to = "%s" % parent_address
    message.body = """Hi, %s
    Your payment of $%s to  %s is being processed. Another email will be sent if the payment is completed.""" % (parent_name, amount, school_name)

    message.send()

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

def send_funding_source_removal_email(email_address, name, funding_source_name, sender_address="rongjian@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Joobali: You have successfully removed funding source - %s." % funding_source_name)

    message.to = "%s" % email_address
    message.body = """Hi, %s
    You have successfully removed funding source - %s.""" % (name, funding_source_name)

    message.send()

def send_funding_source_addition_email(email_address, name, funding_source_name,
                                      sender_address="rongjian@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Joobali: You have successfully added funding source - %s." % funding_source_name)

    message.to = "%s" % email_address
    message.body = """Hi, %s
    You have successfully added funding source - %s.""" % (name, funding_source_name)

    message.send()