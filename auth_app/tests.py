"""API tests for authentication-related endpoints."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterApiTests(APITestCase):
    """Tests for the /api/register/ endpoint."""

    def test_register_returns_201_on_success(self):
        """Registration with valid data should create a user."""
        url = reverse("api-register")
        payload = {
            "username": "tester",
            "email": "tester@example.com",
            "password": "secret123",
            "confirmed_password": "secret123",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "User created successfully!")
        self.assertTrue(User.objects.filter(username="tester").exists())

    def test_register_returns_400_on_password_mismatch(self):
        """Registration should fail if passwords do not match."""
        url = reverse("api-register")
        payload = {
            "username": "tester2",
            "email": "tester2@example.com",
            "password": "secret123",
            "confirmed_password": "wrong123",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BaseAuthApiTests(APITestCase):
    """Base setup and helpers for auth API tests."""

    def setUp(self):
        """Create a default test user."""
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
        )

    def login(self):
        """Login the default user and return the response."""
        url = reverse("api-login")
        payload = {"username": self.user.username, "password": self.password}
        return self.client.post(url, payload, format="json")


class LoginApiTests(BaseAuthApiTests):
    """Tests for the /api/login/ endpoint."""

    def test_login_returns_200_and_sets_cookies(self):
        """Login should succeed and set auth cookies."""
        url = reverse("api-login")
        payload = {"username": self.user.username, "password": self.password}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Login successfully!")
        self.assertIn("user", response.data)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_with_invalid_credentials_returns_401(self):
        """Invalid credentials should result in 401."""
        url = reverse("api-login")
        payload = {"username": self.user.username, "password": "wrong-pass"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutApiTests(BaseAuthApiTests):
    """Tests for the /api/logout/ endpoint."""

    def test_logout_returns_200_when_authenticated(self):
        """Logout should succeed for an authenticated user."""
        login_response = self.login()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        url = reverse("api-logout")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data["detail"].startswith("Log-Out successfully!")
        )

    def test_logout_without_auth_returns_401(self):
        """Logout without authentication should return 401."""
        self.client.cookies.clear()
        url = reverse("api-logout")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshApiTests(BaseAuthApiTests):
    """Tests for the /api/token/refresh/ endpoint."""

    def test_refresh_returns_200_with_valid_cookie(self):
        """Refresh should succeed with a valid refresh token."""
        login_response = self.login()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        url = reverse("token-refresh")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Token refreshed")
        self.assertIn("access", response.data)

    def test_refresh_without_cookie_returns_401(self):
        """Refresh without cookie should return 401."""
        self.client.cookies.clear()
        url = reverse("token-refresh")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Refresh token not found")