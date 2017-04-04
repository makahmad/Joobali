from models import VerificationToken


def get_password_reset_token(token_id):
    return _get_verification_token(token_id, 'password_reset')


def get_provider_email_verification_token(token_id):
    return _get_verification_token(token_id, 'provider_email')


def get_parent_signup_verification_token(token_id):
    return _get_verification_token(token_id, 'parent_signup')


def _get_verification_token(token_id, token_type):
    verification_token = VerificationToken.generate_key(token_id=token_id).get()
    if verification_token is None:
        return None
    if verification_token.type == token_type:
        return verification_token
    return False
