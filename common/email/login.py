from google.appengine.api import mail

def send_reset_password_email(receiver_name, receiver_address, template, sender_address="howdy@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Joobali password reset for %s" % (receiver_address))

    message.to = "%s <%s>" % (receiver_name, receiver_address)
    message.body = """Please contact howdy@joobali.com for Joobali password reset for %s (%s).
""" % (receiver_name, receiver_address)

    message.html = template
    message.send()

    # [END send_mail]