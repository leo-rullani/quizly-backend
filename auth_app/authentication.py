"""Custom authentication that reads JWTs from HttpOnly cookies."""

from __future__ import annotations

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate using Authorization header or access_token cookie."""

    def authenticate(self, request):
        """Return user and token if a valid JWT is found."""
        header = self.get_header(request)
        if header is not None:
            try:
                return super().authenticate(request)
            except (InvalidToken, AuthenticationFailed):
                # Treat invalid header tokens as anonymous
                return None

        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except InvalidToken:
            # Expired or invalid cookie token → behave as unauthenticated
            return None

        return self.get_user(validated_token), validated_token