from django import template
from django.shortcuts import render_to_response

from verification_util import get_provider_email_verification_token


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
        context["loginUrl"] = request.get_host() + "/login"

    return render_to_response(
        'verification/provider_verification_status.html',
        context,
        template.RequestContext(request)
    )
