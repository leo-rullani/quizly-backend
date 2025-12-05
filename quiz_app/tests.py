"""API tests for quiz creation and quiz management."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from quiz_app.models import Quiz

User = get_user_model()


class BaseQuizApiTests(APITestCase):
    """Base setup and helpers for quiz API tests."""

    def setUp(self):
        """Create a default user used across quiz tests."""
        self.password = "quizpassword123"
        self.user = User.objects.create_user(
            username="quizuser",
            email="quiz@example.com",
            password=self.password,
        )

    def login(self):
        """Login the default user and return the response."""
        url = reverse("api-login")
        payload = {"username": self.user.username, "password": self.password}
        return self.client.post(url, payload, format="json")


class CreateQuizApiTests(BaseQuizApiTests):
    """Tests for the /api/createQuiz/ endpoint."""

    def test_create_quiz_requires_authentication(self):
        """Unauthenticated request should return 401."""
        url = reverse("create-quiz")
        payload = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("quiz_app.api.views.create_quiz_from_youtube_url")
    def test_create_quiz_returns_201_with_valid_url(self, mock_create_quiz):
        """Authenticated user can create a quiz from a valid URL."""
        quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="Created in test.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        mock_create_quiz.return_value = quiz
        self.login()
        url = reverse("create-quiz")
        payload = {"url": "https://www.youtube.com/watch?v=example"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], quiz.id)
        self.assertEqual(response.data["video_url"], quiz.video_url)


class QuizListApiTests(BaseQuizApiTests):
    """Tests for the /api/quizzes/ endpoint."""

    def setUp(self):
        """Prepare user and a sample quiz."""
        super().setUp()
        self.quiz = Quiz.objects.create(
            user=self.user,
            title="List Quiz",
            description="For list endpoint.",
            video_url="https://www.youtube.com/watch?v=example",
        )

    def test_list_quizzes_requires_authentication(self):
        """Unauthenticated list request should return 401."""
        url = reverse("quiz-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_quizzes_returns_only_user_quizzes(self):
        """List should return only quizzes belonging to the user."""
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="otherpass123",
        )
        Quiz.objects.create(
            user=other_user,
            title="Other Quiz",
            description="Should not be visible.",
            video_url="https://www.youtube.com/watch?v=other",
        )
        self.login()
        url = reverse("quiz-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.quiz.id)


class QuizDetailApiTests(BaseQuizApiTests):
    """Tests for /api/quizzes/{id}/ detail, patch and delete."""

    def setUp(self):
        """Prepare user and sample quizzes."""
        super().setUp()
        self.own_quiz = Quiz.objects.create(
            user=self.user,
            title="Own Quiz",
            description="Owned by quizuser.",
            video_url="https://www.youtube.com/watch?v=own",
        )
        self.other_user = User.objects.create_user(
            username="someone_else",
            email="else@example.com",
            password="elsepass123",
        )
        self.other_quiz = Quiz.objects.create(
            user=self.other_user,
            title="Other Quiz",
            description="Foreign quiz.",
            video_url="https://www.youtube.com/watch?v=foreign",
        )

    def test_quiz_detail_requires_authentication(self):
        """Unauthenticated detail request should return 401."""
        url = reverse("quiz-detail", args=[self.own_quiz.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_quiz_detail_returns_own_quiz(self):
        """Authenticated user can retrieve own quiz."""
        self.login()
        url = reverse("quiz-detail", args=[self.own_quiz.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.own_quiz.id)

    def test_quiz_detail_returns_403_for_foreign_quiz(self):
        """Accessing another user's quiz should return 403."""
        self.login()
        url = reverse("quiz-detail", args=[self.other_quiz.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_quiz_detail_returns_404_for_unknown_id(self):
        """Unknown quiz id should return 404."""
        self.login()
        url = reverse("quiz-detail", args=[999999])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_quiz_patch_updates_title(self):
        """PATCH should update title for own quiz."""
        self.login()
        url = reverse("quiz-detail", args=[self.own_quiz.id])
        payload = {"title": "Updated Title"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")

    def test_quiz_delete_own_quiz_returns_204(self):
        """DELETE should remove own quiz and return 204."""
        self.login()
        url = reverse("quiz-detail", args=[self.own_quiz.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Quiz.objects.filter(id=self.own_quiz.id).exists()
        )