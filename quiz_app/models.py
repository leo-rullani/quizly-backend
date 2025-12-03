"""Database models for quizzes and questions in the Quizly app."""

from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """Represents a quiz generated from a YouTube video for a single user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Return the quiz title for readable representations."""
        return self.title


class Question(models.Model):
    """Represents a single question that belongs to a specific quiz."""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_title = models.CharField(max_length=500)
    question_options = models.JSONField()
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Return a readable representation for admin and debugging."""
        return f"{self.quiz.title}: {self.question_title[:50]}"