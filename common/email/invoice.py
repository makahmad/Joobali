import os
import logging
from google.appengine.api import mail
from django.template import loader

logger = logging.getLogger(__name__)
module_dir = os.path.dirname(__file__)

# TODO(zilong): Refine the html template with proper input parameters
_enrollment_notification_template = loader.get_template('enrollment/enrollment_notification_template.html')
_signup_notification_template = loader.get_template('enrollment/signup_invitation_template.html')


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
    program = enrollment.program_key.get()
    child = enrollment.child_key.get()

    is_parent_signup = parent.invitation.token is None
    parent_email = parent.email
    signup_url = "http://" + host + "/login/parentsignup" + parent.invitation.link
    provider_name = provider.schoolName
    # [START send_mail]
    message = mail.EmailMessage(
        sender=sender_address,
        subject="Invitation from %s to make payments online." % provider_name)

    message.to = "%s" % parent_email
    logger.info('resending invitation to %s' % parent_email)
    if not is_parent_signup:
        global _signup_notification_template
        rendering_data = {
            'host': host,
            'provider_school_name': provider.schoolName,
            'program_name': program.programName,
            'child_first_name': child.first_name,
            'enrollment_start_date': enrollment.start_date,
            'signup_url': signup_url,
        }
        message.html = _signup_notification_template.render(rendering_data)
    else:
        global _enrollment_notification_template
        rendering_data = {
            'provider_school_name' : provider.schoolName,
            'program_name' : program.programName
        }
        message.html = _enrollment_notification_template.render(rendering_data)
    message.send()

    # [END send_mail]

