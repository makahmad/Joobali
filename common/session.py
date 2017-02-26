"""Package for common session management method"""


# TODO(zilong): check against session stored in datastore
def check_session(request):
    """This method will check session for a HTTP Request"""
    if not request.session.get('user_id'):
        return False
    else:
        return True


def is_provider(request):
    return request.session.get('is_provider')


def get_provider_email(request):
    if is_provider(request):
        return request.session.get("email")
    else:
        raise RuntimeError("Cannot get provider email from a non-provider session")


def get_provider_id(request):
    if is_provider(request):
        return request.session.get("user_id")
    else:
        raise RuntimeError("Cannot get provider id from a non-provider session")