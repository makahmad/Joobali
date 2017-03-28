from django.http import HttpResponse

from verification_util import get_provider_email_verification_token

def verify_provider_email(request):
    if request.method != 'GET':
        return
    token_id = request.GET['t']
    token = get_provider_email_verification_token(token_id)
    if token is not None:
        provider = token.provider_key.get()
        provider.status.status = 'active'
        provider.put()
        token.key.delete()
        return HttpResponse('Verification Successful')
    return HttpResponse('Verification Failed')

