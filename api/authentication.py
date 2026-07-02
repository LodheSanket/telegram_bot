"""
Custom authentication for the API. Instead of user accounts and
passwords, every request just needs to include a shared secret key
in the X-API-KEY header. This fits the use case here: the only
client is the Telegram bot, not individual end users.
"""

from django.conf import settings
from rest_framework import authentication, exceptions


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            raise exceptions.AuthenticationFailed("Missing API key. Include an X-API-KEY header.")

        if api_key != settings.SECRET_API_KEY:
            raise exceptions.AuthenticationFailed("Invalid API key.")

        # There's no real user model behind this API, so we return
        # (None, None). DRF only cares that we didn't raise, which
        # means the request is allowed through.
        return (None, None)

    def authenticate_header(self, request):
        # Returning a value here is what makes DRF respond with 401
        # instead of 403 when authentication fails. Without this,
        # AuthenticationFailed defaults to a 403 response.
        return "X-API-KEY"
