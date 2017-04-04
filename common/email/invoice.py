import logging
from os import environ

from google.appengine.api import mail
from django.template import Context, loader
from google.appengine.runtime.apiproxy_errors import OverQuotaError

logger = logging.getLogger(__name__)

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


def send_parent_enrollment_notify_email(enrollment, host, sender_address="howdy@joobali.com", verification_token=None):
    provider = enrollment.key.parent().get()
    parent = enrollment.child_key.get().parent_key.get()
    program = enrollment.program_key.get()
    child = enrollment.child_key.get()

    is_parent_signup = (parent.status == 'active')
    parent_email = parent.email
    http_prefix = 'http://' if environ.get('IS_DEV') else 'https://'
    provider_name = provider.schoolName

    message = mail.EmailMessage(
        sender=sender_address,
        subject="Invitation from %s to make payments online." % provider_name)

    message.to = "%s" % parent_email
    if not is_parent_signup:
        signup_url = http_prefix + host + "/login/parentsignup?t=" + verification_token.token_id
        logger.info('sending signup invitation to %s' % parent_email)
        global _signup_notification_template
        rendering_data = {
            'host': host,
            'provider_school_name': provider.schoolName,
            'program_name': program.programName,
            'child_first_name': child.first_name,
            'enrollment_start_date': enrollment.start_date,
            'program_fee': program.fee,
            'program_billing_cycle': program.billingFrequency,
            'signup_url': signup_url,
        }
        message.html = _signup_notification_template.render(Context(rendering_data))
    else:
        logger.info('sending enrollment invitation to %s' % parent_email)
        enrollment_detail_url = http_prefix + host + "/parent/#!/enrollmentview/" + ("%d/%d" % (
            provider.key.id(), enrollment.key.id()))
        global _enrollment_notification_template
        rendering_data = {
            'host': host,
            'provider_school_name': provider.schoolName,
            'program_name': program.programName,
            'child_first_name': child.first_name,
            'enrollment_start_date': enrollment.start_date,
            'enrollment_detail_url': enrollment_detail_url,
            'program_billing_frequency': program.billingFrequency
        }
        message.html = _enrollment_notification_template.render(Context(rendering_data))
    try:
        message.send()
        return True
    except OverQuotaError:
        logger.error("Getting over quota error when sending enrollmen")
        return False

