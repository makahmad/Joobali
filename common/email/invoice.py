import os
import logging
from google.appengine.api import mail
from django.template import Context, Template

logger = logging.getLogger(__name__)
module_dir = os.path.dirname(__file__)

# TODO(zilong): Refine the html template with proper input parameters
_enrollment_notification_template = Template(
    open(module_dir + '/html_template/enrollment_notification_template.html').read())
_signup_notification_template = Template(open(module_dir + '/html_template/signup_invitation_template.html').read())


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


def send_parent_enrollment_notify_email(enrollment, host, sender_address="zilong@joobali.com"):
    provider = enrollment.key.parent().get()
    parent = enrollment.child_key.get().parent_key.get()
    program = enrollment.program_key.get()

    is_parent_signup = parent.invitation.token is None
    parent_email = parent.email
    signup_url = "http://" + host + "/login/parentsignup" + parent.invitation.link
    provider_name = provider.schoolName
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Invitation from %s to make payments online." % provider_name)

    message.to = "%s" % "zilong@joobali.com"
    if not is_parent_signup:
        global _signup_notification_template
        context = Context({
            'provider_school_name': provider.schoolName,
            'signup_url': signup_url,
        })
        message.html = _signup_notification_template.render(context)
    else:
        global _enrollment_notification_template
        context = Context({
            'provider_school_name' : provider.schoolName,
            'program_name' : program.programName
        })
        message.html = _enrollment_notification_template.render(context)
    logger.info(message.html)
    message.send()

    # [END send_mail]

