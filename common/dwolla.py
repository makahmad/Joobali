"""Package for common dwolla related helper methods and constants"""
import dwollav2

# Client constants
CLIENT_ID = 'g36djuD0XBwoDteIjEz9fcGKsKJbWN72IW8wmXBZA5glcSUhg9'
CLIENT_SECRET = '3clqlV4LrOf7udsCjuYs9ONnN1Eq78a0OcNvpUWcCBK5PTNkQ9'
DEFAULT_ENVIRONMENT = 'sandbox'

# Account constants
ACCESS_TOKEN = 'UZjwsTujbiEVxi0egVgWHACt1vT5tQckyE1uj1gaqNxwL0TwOB'
REFRESH_TOKEN = 'o9tuD34y19J7yw86lDratuOCdD4Ngmq5xqOLJqTiBAIK4LEqke'

def create_account_token(environment):
    client = dwollav2.Client(id=CLIENT_ID, secret=CLIENT_SECRET, environment=environment)
    return client.Token(access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
