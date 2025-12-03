"""URL routes for authentication and token endpoints."""

from django.urls import path

from .views import (
    CookieRefreshView,
    CookieTokenObtainPairView,
    LogoutView,
    RegistrationView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="api-register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="api-login"),
    path("logout/", LogoutView.as_view(), name="api-logout"),
    path("token/refresh/", CookieRefreshView.as_view(), name="token-refresh"),
]