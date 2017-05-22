import logging
from google.appengine.api import mail

logger = logging.getLogger(__name__)

def send_payment_created_email(parent_address, parent_name, school_name, amount, template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Your payment to %s is created." % school_name)

    message.to = "%s" % parent_address
    message.body = """Hi, %s
    Your payment of $%s to  %s is created. Another email will be sent if the payment is completed.""" % (parent_name, amount, school_name)

    message.html = template
    message.send()

def send_payment_success_email(parent_address, parent_name, school_name, amount, template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="You have successfully paid <%s> $%s.""" % (school_name, amount))

    message.to = "%s" % parent_address
    message.body = """Hi, %s
    You've successfully paid <%s> with $%s.""" % (parent_name, school_name, amount)

    message.html = template
    message.send()



def send_payment_failure_email(parent_address, parent_name, school_name, amount, template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Your payment to %s failed.""" % (school_name))

    message.to = "%s" % parent_address
    message.body = """Hi, %s
    Your payment of $%s to <%s> was denied by the bank. Please try again.""" % (parent_name, school_name, amount)

    message.html = template
    message.send()

def send_payment_cancelled_email(parent_address, parent_name, school_name, amount, template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Your payment to %s was cancelled.""" % (school_name))

    message.to = "%s" % parent_address
    message.body = """Hi, %s
    Your payment of $%s to <%s> is successfully cancelled.""" % (parent_name, school_name, amount)

    message.html = template
    message.send()

def send_funding_source_removal_email(email_address, name, funding_source_name, template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Joobali: You have successfully removed funding source - %s." % funding_source_name)

    message.to = "%s" % email_address
    message.body = """Hi, %s
    You have successfully removed funding source - %s.""" % (name, funding_source_name)

    message.html = template
    message.send()

def send_funding_source_addition_email(email_address, name, funding_source_name, template,
                                      sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Joobali: You have successfully added funding source - %s." % funding_source_name)

    message.to = "%s" % email_address
    message.body = """Hi, %s
    You have successfully added funding source - %s.""" % (name, funding_source_name)

    message.html = template
    message.send()