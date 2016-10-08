"""Package for common session management method"""


def check_session(request):
    """This method will check session for a HTTP Request"""
    if not request.session.get('email'):
        return False
    else:
        return True
