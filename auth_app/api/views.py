"""API views for user registration, login, logout and token refresh."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from auth_app.utils.auth_cookies import (
    blacklist_refresh_cookie,
    clear_auth_cookies,
    set_auth_cookies,
)
from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer

LOGOUT_MESSAGE = (
    "Log-Out successfully! All Tokens will be deleted. "
    "Refresh token is now invalid."
)


class RegistrationView(APIView):
    """Handle user registration."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate data and create a new user."""
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        data = {"detail": "User created successfully!"}
        return Response(data, status=status.HTTP_201_CREATED)


class CookieTokenObtainPairView(TokenObtainPairView):
    """Issue JWT tokens, store them in cookies and return user data."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate user by email and set JWT cookies."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]
        user_data = serializer.validated_data["user"]
        response = Response(
            {"detail": "Login successfully!", "user": user_data},
            status=status.HTTP_200_OK,
        )
        set_auth_cookies(response, str(access), str(refresh))
        return response


class CookieRefreshView(TokenRefreshView):
    """Refresh the access token using the refresh cookie."""

    def post(self, request, *args, **kwargs):
        """Issue a new access token and update cookie."""
        refresh = request.COOKIES.get("refresh_token")
        if not refresh:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = self.get_serializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data["access"]
        response = Response(
            {"detail": "Token refreshed", "access": str(access)},
            status=status.HTTP_200_OK,
        )
        set_auth_cookies(response, str(access), refresh)
        return response


class LogoutView(APIView):
    """Log out the user and invalidate their tokens."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist refresh token and clear auth cookies."""
        refresh = request.COOKIES.get("refresh_token")
        blacklist_refresh_cookie(refresh)
        response = Response({"detail": LOGOUT_MESSAGE}, status=status.HTTP_200_OK)
        clear_auth_cookies(response)
        return response