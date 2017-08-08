import logging

from django.http import HttpResponseNotFound
from django.shortcuts import render

from common.email.login import send_provider_email_address_verification
from common.request import get_host_from_request
from login.models import Unique
from verification_util import get_provider_email_verification_token, list_provider_email_verification_token, \
    create_provider_email_verification_token

logger = logging.getLogger(__name__)


def verify_provider_email(request):
    if request.method != 'GET':
        return
    token_id = request.GET['t']
    token = get_provider_email_verification_token(token_id)
    context = {
        'verification_status': "unsuccessful",
        'email': "N/A",
        'school_name': "N/A"
    }

    if token is not None:
        provider = token.provider_key.get()
        provider.status.status = 'active'
        provider.put()
        token.key.delete()
        context["status"] = 'successful'
        context["email"] = provider.email
        context["schoolName"] = provider.schoolName
        return render(
            request,
            'verification/provider_verification_status.html',
            context
        )
    else:
        return HttpResponseNotFound("invalid email verification token")


def resend_provider_email_verification(request):
    if request.method == 'GET':
        return render(
            request,
            'verification/provider/resend_email_verification.html'
        )

    if request.method == 'POST':
        payload = request.POST
        email = payload['email']
        unique = Unique.get_by_id(email)
        result = {
            'resend_result': {
                'email_not_found': True,
                'provider_not_found': True,
                'resend_status': False,
            },
            'email': email
        }
        if unique is not None:
            logger.info("Find account with email %s" % email)
            result['resend_result']['email_not_found'] = False
            if unique.provider_key is not None:
                result['resend_result']['provider_not_found'] = False
                verification_tokens = list_provider_email_verification_token(unique.provider_key)
                tokens = list()
                for token in verification_tokens:
                    tokens.append(token)
                if len(tokens) == 0:
                    verification_token = create_provider_email_verification_token(unique.provider_key)
                else:
                    verification_token = tokens[0]
                send_provider_email_address_verification(verification_token=verification_token,
                                                         host=get_host_from_request(request.get_host()))
                result['resend_result']['resend_status'] = True

        return render(
            request,
            'verification/provider/resend_email_verification.html',
            result
        )

