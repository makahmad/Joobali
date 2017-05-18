class JoobaliRpcException(Exception):
    """
    RpcException that helps surface the error to the client and developer.
    """
    def __init__(self, error_code=400, client_viewable_message="", error_message=""):
        """
        
        :param error_code: Http Error code to be surfaced to user
        :param error_message: internal error message, should not be displayed to external user
        :param client_viewable_message: message that can be presented to external user
        """
        self._error_code = error_code
        self._error_message = error_message
        self._client_viewable_message = client_viewable_message

    def get_http_error_code(self):
        return self._error_code

    def get_client_messasge(self):
        return self._client_viewable_message

    def get_error_message(self):
        return self._error_message
