from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegistrationSerializer, CustomObjectSerializer


class RegistrationView(APIView):
    """
    API endpoint that allows new users to register.

    Expected request body (JSON):
    - username: string
    - email: string (must be unique)
    - password: string
    - repeated_password: string (must be equal to password)

    Responses:
    - 201 Created: user data (username, email, user_id)
    - 400 Bad Request: validation errors
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests to create a new user account.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            data = {
                "username": saved_account.username,
                "email": saved_account.email,
                "user_id": saved_account.pk,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom TokenObtainPairView that sets the JWT tokens in HttpOnly cookies
    and uses email + password for authentication.
    """

    serializer_class = CustomObjectSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user login using email and password.

        Expected body:
        - email
        - password
        """
        # Use our custom serializer (email + password)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data.get("refresh")
        access = serializer.validated_data.get("access")

        # Build a custom response without exposing the tokens
        response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)

        # In der Kurs-Variante: secure=True + ggf. SSL-Verification in Postman
        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response


class CookieRefreshView(TokenRefreshView):
    """
    Refresh view that reads the refresh token from a HttpOnly cookie
    and issues a new access token, also stored as a HttpOnly cookie.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"error": "Refresh token not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"error": "Refresh token invalid"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")
        response = Response(
            {"message": "Access token refreshed successfully"},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response