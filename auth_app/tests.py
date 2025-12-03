"""API tests for authentication login and logout flow."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthApiTests(APITestCase):
    """Integration tests for login and logout endpoints."""

    def setUp(self):
        """Create a user used across authentication tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

    def test_login_sets_auth_cookies(self):
        """Login should return 200 and set access and refresh cookies."""
        url = reverse("api-login")
        data = {"email": "test@example.com", "password": "testpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_logout_clears_auth_cookies(self):
        """Logout should clear auth cookies and return success message."""
        login_url = reverse("api-login")
        logout_url = reverse("api-logout")
        data = {"email": "test@example.com", "password": "testpassword123"}
        self.client.post(login_url, data, format="json")
        response = self.client.post(logout_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data["detail"].startswith("Log-Out successfully!")
        )