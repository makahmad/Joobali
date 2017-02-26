from google.appengine.api import mail
from string import Formatter


def send_invoice_email(parent_address, invoice, start_date, end_date, template, sender_address="rongjian@joobali.com"):
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


def send_parent_enrollment_notify_email(enrollment, host, sender_address="rongjian@joobali.com"):
    provider = enrollment.key.parent().get()
    parent = enrollment.child_key.get().parent_key.get()

    is_parent_signup = parent.invitation.token is None
    parent_email = parent.email
    signup_url = host + "/login/parentsignup" + parent.invitation.link
    provider_name = provider.schoolName
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Invitation from %s to make payments online." % provider_name)

    message.to = "%s" % parent_email

    message.body = "%s has invited you to make payments online and view invoices for child care services provided."
    message.body = message.body % provider_name

    program_info = "the program is %s" % enrollment.program_key.get().programName

    message.body += program_info

    if is_parent_signup:
        message.body += "Please sign up and make a payment via Joobli on or before the due date indicated."
        message.body += ("If you do not pay online, be sure to pay %s in person by check or cash." % provider_name)
        message.body += "Don't forget, late fees may be incurred if payments are not made on time."
        message.body += ("Signup link: (%s)" % signup_url)

    message.send()

    # [END send_mail]

