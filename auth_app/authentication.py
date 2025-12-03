"""Custom authentication that reads JWTs from HttpOnly cookies."""

from __future__ import annotations

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate using Authorization header or access_token cookie."""

    def authenticate(self, request):
        """Return user and token if a valid JWT is found."""
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token