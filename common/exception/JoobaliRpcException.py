class JoobaliRpcException(Exception):
    """
    RpcException that helps surface the error to the client and developer.
    """
    def __init__(self, error_message, client_viewable_message):
        """
        :param error_message: internal error message, should not be displayed to external user
        :param client_viewable_message: message that can be presented to external user
        """
        self._error_message = error_message
        self._client_viewable_message = client_viewable_message

    def get_client_messasge(self):
        return self._client_viewable_message

    def get_error_message(self):
        return self._error_message
