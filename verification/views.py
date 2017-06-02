import logging
from django import template
from django.http import HttpResponseNotFound
from django.shortcuts import render

from verification_util import get_provider_email_verification_token

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
        # token.key.delete()
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

