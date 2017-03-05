from google.appengine.api import mail

def send_referral_email(receiver_name, receiver_address, referrer_name, template, sender_address="howdy@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="%s has been invited to join Joobali by %s" % (receiver_name, referrer_name))

    message.to = "%s <%s>" % (receiver_name, receiver_address)
    message.body = """%s has been invited to join Joobali by %s. Joobali is transforming childcare management technology by putting childcare providers first so they can focus on more important things.
""" % (receiver_name, receiver_address)

    message.html = template
    message.send()

    # [END send_mail]
