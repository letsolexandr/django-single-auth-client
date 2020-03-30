from rest_framework.authentication import TokenAuthentication
from rest_framework import HTTP_HEADER_ENCODING, exceptions



class SyncClientAuthentication(TokenAuthentication):
    def __init__(self):
        from .client import Client
        self.client = Client()
        super(SyncClientAuthentication, self).__init__()

    def authenticate_credentials(self, key):
        if key:
            is_valid, client_errors = self.client.run_validation(key)
            if is_valid:
                return super(SyncClientAuthentication, self).authenticate_credentials(key)
            else:
                raise exceptions.AuthenticationFailed(client_errors)
        else:
            return exceptions.AuthenticationFailed('Authorization  token not set')
