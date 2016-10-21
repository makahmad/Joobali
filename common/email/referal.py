from google.appengine.api import mail

def send_referal_email(receiver_name, receiver_address, referer_name, sender_address="howdy@joobali.com", ):
    # [START send_mail]
    mail.send_mail(sender=sender_address,
                   to="%s <%s>" % (receiver_name, receiver_address),
                   subject="%s has been invited to join Joobali by %s" % (receiver_name, referer_name),
                   body="""%s has been invited to join Joobali by %s. Joobali is transforming childcare management technology by putting childcare providers first so they can focus on more important things.
""" % (receiver_name, receiver_address))
    # [END send_mail]
