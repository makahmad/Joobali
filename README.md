# Joobali
Joobali backend and frontend code


Run the following python code in interactive console (http://localhost:8000/console) to import Dwolla access token

```python
from tasks.models import DwollaTokens

token = DwollaTokens()
token.access_token = '' # Replace with the access token you have
token.refresh_token = '' # Replace with the refresh token you have
token.put()
```