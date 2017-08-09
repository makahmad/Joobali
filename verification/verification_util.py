from models import VerificationToken


def get_password_reset_token(token_id):
    return _get_verification_token(token_id, 'password_reset')


def get_provider_email_verification_token(token_id):
    return _get_verification_token(token_id, 'provider_email')


def list_provider_email_verification_token(provider_key):
    return VerificationToken.list_provider_email_token(provider_key.get())


def create_provider_email_verification_token(provider_key):
    verification_token = VerificationToken.create_new_provider_email_token(provider_key.get())
    verification_token.put()
    return verification_token

def get_parent_signup_verification_token(token_id=None, parent_key=None):
    """
    If token_id is specified, a unique VerificationToken with type 'parent_signup' will be returned.
    If parent_key is specified, a list of VerificationToken with the parent_key and type 'parent_signup' will be 
    returned
    :param token_id: 
    :param parent_key: 
    :return: 
    """
    if token_id is not None:
        return _get_verification_token(token_id, 'parent_signup')
    if parent_key is not None:
        query = VerificationToken.query(VerificationToken.parent_key == parent_key,
                                        VerificationToken.type == 'parent_signup')
        result = list()
        for verification_token in query:
            result.append(verification_token)
        return result


def _get_verification_token(token_id, token_type):
    verification_token = VerificationToken.generate_key(token_id=token_id).get()
    if verification_token is None:
        return None
    if verification_token.type == token_type:
        return verification_token
    return False
