import logging
from common.email.utils import send_email

logger = logging.getLogger(__name__)


def send_payment_created_email(parent_address, parent_name, school_name, amount, template,
                               sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "Your payment to %s is created." % school_name

    email_to = "%s" % parent_address
    # TODO(rongjian): check if we really need this body anymore
    email_body = """Hi, %s
    Your payment of $%s to  %s is created. Another email will be sent if the payment is completed.""" % (
    parent_name, amount, school_name)

    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_payment_created_email_to_provider(provider_address, provider_name, parent_name, school_name, amount, template,
                                           sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]

    email_subject = "A payment to %s is created." % school_name
    email_to = "%s" % provider_address
    email_body = """Hi, %s
    Parent %s created a payment of amount $%s to you. Another email will be sent if the payment is completed.""" % (
    provider_name, parent_name, amount)
    email_html = template

    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_payment_success_email(parent_address, parent_name, school_name, amount, template,
                               sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "You have successfully paid %s $%s.""" % (school_name, amount)
    email_to = "%s" % parent_address
    email_body = """Hi, %s
    You've successfully paid %s with $%s.""" % (parent_name, school_name, amount)
    email_html = template

    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_payment_success_email_to_provider(provider_address, provider_name, parent_name, school_name, amount, template,
                                           sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "The payment of $%s from %s succeeded." % (amount, parent_name)
    email_to = "%s" % provider_address
    email_body = """Hi, %s
    Parent %s's payment of amount $%s to you is completed successfully.""" % (provider_name, parent_name, amount)
    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_payment_failed_email(parent_address, parent_name, school_name, amount, template,
                              sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "Your payment to %s failed.""" % (school_name)
    email_to = "%s" % parent_address
    email_body = """Hi, %s
    Your payment of $%s to %s was denied by the bank. Please try again.""" % (parent_name, school_name, amount)
    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_payment_failed_email_to_provider(provider_address, provider_name, parent_name, school_name, amount, template,
                                          sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "The payment of $%s from %s failed." % (amount, parent_name)
    email_to = "%s" % provider_address
    email_body = """Hi, %s
    Parent %s's payment of amount $%s to you failed.""" % (provider_name, parent_name, amount)
    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_payment_cancelled_email(parent_address, parent_name, school_name, amount, template,
                                 sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "Your payment to %s was cancelled.""" % (school_name)
    email_to = "%s" % parent_address
    email_body = """Hi, %s
    Your payment of $%s to %s is successfully cancelled.""" % (parent_name, school_name, amount)
    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_payment_cancelled_email_to_provider(provider_address, provider_name, parent_name, school_name, amount,
                                             template, sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]

    email_subject = "The payment of $%s from %s was cancelled." % (amount, parent_name)

    email_to = "%s" % provider_address
    email_body = """Hi, %s
    Parent %s's payment of amount $%s to you was cancelled.""" % (provider_name, parent_name, amount)
    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_funding_source_removal_email(email_address, name, funding_source_name, template,
                                      sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "Joobali: You have successfully removed a bank account - %s." % funding_source_name
    email_to = "%s" % email_address
    email_body = """Hi, %s
    You have successfully removed bank account - %s.""" % (name, funding_source_name)
    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)


def send_funding_source_addition_email(email_address, name, funding_source_name, template,
                                       sender_address="Joobali <howdy@joobali.com>"):
    # [START send_mail]
    email_subject = "Joobali: You have successfully added bank account - %s." % funding_source_name
    email_to = "%s" % email_address
    email_body = """Hi, %s
    You have successfully added bank account - %s.""" % (name, funding_source_name)
    email_html = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html, body=email_body)
