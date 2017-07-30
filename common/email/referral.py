from common.email.utils import send_email


def send_referral_email(receiver_name, receiver_address, referrer_name, template, sender_address="Joobali <howdy@joobali.com>"):
    email_subject = "%s has been invited to join Joobali by %s" % (receiver_name, referrer_name)
    email_to = "%s <%s>" % (receiver_name, receiver_address)
    email_body = """%s has been invited to join Joobali by %s. Joobali is transforming childcare management technology by putting childcare providers first so they can focus on more important things.
""" % (receiver_name, receiver_address)

    email_html_content = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html_content, body=email_body)


def send_provider_referral_email(receiver_name, receiver_address, referrer_name, template, sender_address="Joobali <howdy@joobali.com>"):
    email_subject="%s has been invited to join Joobali by %s" % (receiver_name, referrer_name)

    email_to = "%s <%s>" % (receiver_name, receiver_address)
    email_body = """%s has been invited to join Joobali by %s. Joobali is transforming childcare management technology by putting childcare providers first so they can focus on more important things.
""" % (receiver_name, receiver_address)

    email_html_content = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, body=email_body, html_content=email_html_content)


def send_parent_referral_email(receiver_name, receiver_address, referrer_name, template, sender_address="Joobali <howdy@joobali.com>"):
    email_subject="%s has been invited to join Joobali by %s" % (receiver_name, referrer_name)
    email_to = "%s <%s>" % (receiver_name, receiver_address)
    email_body = """%s has been invited to join Joobali by %s. Joobali is transforming childcare management technology by putting childcare providers first so they can focus on more important things.
""" % (receiver_name, receiver_address)

    email_html_content = template
    send_email(sender=sender_address, to=email_to, subject=email_subject, body=email_body, html_content=email_html_content)

