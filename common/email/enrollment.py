import logging
from os import environ

from django.template import Context, loader
from google.appengine.runtime.apiproxy_errors import OverQuotaError
from common import datetime_util
from common.email.utils import send_email

from verification import verification_util

logger = logging.getLogger(__name__)

_enrollment_notification_template = loader.get_template('enrollment/enrollment_notification_template.html')
_signup_notification_template = loader.get_template('enrollment/signup_invitation_template.html')


def send_unenroll_email(enrollment, host, sender_address="Joobali <howdy@joobali.com>"):
    child = enrollment.child_key.get()
    parent = child.parent_key.get()
    program = enrollment.program_key.get()
    provider = enrollment.key.parent().get()
    provider_name = provider.schoolName
    parent_email = parent.email

    email_subject = "Invitation from %s to make payments online." % provider_name
    email_to = "%s" % parent_email

    http_prefix = 'http://' if environ.get('IS_DEV') == 'True' else 'https://'
    enrollment_detail_url = http_prefix + host + "/parent/#!/enrollmentview/" + ("%d/%d" % (
        provider.key.id(), enrollment.key.id()))
    rendering_data = {
        'host': host,
        'provider_school_name': provider.schoolName,
        'program_name': program.programName,
        'child_first_name': child.first_name,
        'enrollment_start_date': datetime_util.utc_to_local(enrollment.start_date).strftime('%m/%d/%Y'),
        'program_fee': enrollment.billing_fee if enrollment.billing_fee else program.fee,
        'program_billing_frequency': program.billingFrequency,
        'enrollment_detail_url': enrollment_detail_url,
        'is_unenroll_reminder': True
    }
    email_html_content = _enrollment_notification_template.render(rendering_data)

    try:
        send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html_content)
        return True
    except OverQuotaError:
        logger.error("Getting over quota error when sending enrollmen")
        return False


def send_parent_enrollment_notify_email(enrollment, host, sender_address="Joobali <howdy@joobali.com>",
                                        verification_token=None):
    provider = enrollment.key.parent().get()
    parent = enrollment.child_key.get().parent_key.get()
    program = enrollment.program_key.get()
    child = enrollment.child_key.get()

    is_parent_signup = (parent.status.status == 'active')
    parent_email = parent.email
    http_prefix = 'http://' if environ.get('IS_DEV') == 'True' else 'https://'
    provider_name = provider.schoolName

    email_subject = "Invitation from %s to make payments online." % provider_name
    email_to = "%s" % parent_email

    if not is_parent_signup:
        if verification_token is None:
            verification_token = verification_util.get_parent_signup_verification_token(parent_key=parent.key)[0]
        signup_url = http_prefix + host + "/login/parentsignup?t=" + verification_token.token_id
        logger.info('sending signup invitation to %s' % parent_email)
        global _signup_notification_template

        rendering_data = {
            'host': host,
            'provider_school_name': provider.schoolName,
            'program_name': program.programName,
            'child_first_name': child.first_name,
            'enrollment_start_date': datetime_util.utc_to_local(enrollment.start_date).strftime('%m/%d/%Y'),
            'start_date': datetime_util.utc_to_local(enrollment.start_date).strftime('%m/%d/%Y'),
            'end_date': datetime_util.utc_to_local(enrollment.end_date).strftime('%m/%d/%Y') if enrollment.end_date else '',
            'program_fee': enrollment.billing_fee if enrollment.billing_fee else program.fee,
            'program_billing_cycle': program.billingFrequency,
            'signup_url': signup_url,
        }
        email_html_content = _signup_notification_template.render(rendering_data)
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
            'enrollment_start_date': datetime_util.utc_to_local(enrollment.start_date).strftime('%m/%d/%Y'),
            'enrollment_detail_url': enrollment_detail_url,
            'program_billing_frequency': program.billingFrequency,
            'is_acceptance_reminder': True,
            'due_date': datetime_util.utc_to_local(enrollment.start_date).strftime('%m/%d/%Y'),
            'amount': enrollment.billing_fee if enrollment.billing_fee else program.fee,
            'start_date': datetime_util.utc_to_local(enrollment.start_date).strftime('%m/%d/%Y'),
            'end_date': datetime_util.utc_to_local(enrollment.end_date).strftime('%m/%d/%Y') if enrollment.end_date else '',
        }
        email_html_content = _enrollment_notification_template.render(rendering_data)
    try:
        send_email(sender=sender_address, to=email_to, subject=email_subject, html_content=email_html_content)
        return True
    except OverQuotaError:
        logger.error("Getting over quota error when sending enrollmen")
        return False
