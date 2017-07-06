"""Package for common request related methods"""


def get_host_from_request(request_host):
    """This method will return the appropriate host name based on request host name. Basically convert joobali-prod.appspot.com to www.joobali.com"""
    if 'prod' in request_host:
        return 'https://www.joobali.com'
    return request_host
