from google.appengine.api import mail

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

    message.html = template;
    message.send()

    # [END send_mail]


def send_parent_invite_email(parent_address, provider_name, sign_up_url, template=None, sender_address="rongjian@joobali.com"):
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Invitation from %s to make payments online." % provider_name)

    message.to = "%s" % parent_address
    message.body = """%s has invited you to make payments online and view invoices for child care services provided.
Please sign up and make a payment via Joobli on or before the due date indicated. If you do not pay online, be sure to pay %s in person by check or cash.
Don't forget, late fees may be incurred if payments are not made on time. (%s)
""" % (provider_name, provider_name, sign_up_url)

    if template:
        message.html = template;
    message.send()

    # [END send_mail]