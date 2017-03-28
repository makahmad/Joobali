from django.http import HttpResponse

from models import VerificationToken


def verify_provider_email(request):
    if request.method != 'GET':
        return
    token_id = request.GET['t']
    token = VerificationToken.generate_key(token_id=token_id).get()
    if token is not None:
        provider = token.provider_key.get()
        provider.status.status = 'active'
        provider.put()
        return HttpResponse('Verification Successful')
    return HttpResponse('Verification Failed')

