"""Package for common session management method"""

# TODO(zilong): check against session stored in datastore
def check_session(request):
    """This method will check session for a HTTP Request"""
    if not request.session.get('user_id'):
        return False
    else:
        return True


def get_provider_email(request):
    return request.session.get("email")


def get_provider_id(request):
    return request.session.get('user_id')
