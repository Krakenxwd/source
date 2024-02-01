from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from registration.models import Client


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        client_id = request.headers.get('Client-Id')
        client_secret = request.headers.get('Client-Secret')

        if not client_id or not client_secret:
            return None

        try:
            client = Client.objects.get(client_id=client_id, client_secret=client_secret)
        except Client.DoesNotExist:
            raise AuthenticationFailed('Invalid client credentials.')

        return client.user, None
