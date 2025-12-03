"""Helpers for managing auth cookies and token blacklisting."""

from __future__ import annotations

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def set_auth_cookies(response: Response, access: str, refresh: str) -> None:
    """Attach access and refresh JWTs to HttpOnly cookies."""
    for name, value in (("access_token", access), ("refresh_token", refresh)):
        response.set_cookie(
            key=name,
            value=value,
            httponly=True,
            secure=True,
            samesite="Lax",
        )


def clear_auth_cookies(response: Response) -> None:
    """Remove auth cookies from the response."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


def blacklist_refresh_cookie(refresh_token: str | None) -> None:
    """Blacklist the given refresh token if possible."""
    if not refresh_token:
        return
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return