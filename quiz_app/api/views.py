"""API views for creating and managing quizzes."""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quiz_app.models import Quiz
from quiz_app.utils.quiz_pipeline import create_quiz_from_youtube_url

from .parsers import PlainTextJSONParser
from .serializers import (
    CreateQuizSerializer,
    QuizSerializer,
    QuizWithTimestampsSerializer,
)


class CreateQuizView(APIView):
    """Create a quiz from a YouTube URL."""

    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        """Validate input and trigger quiz creation."""
        serializer = CreateQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data["url"]
        try:
            quiz = create_quiz_from_youtube_url(url, request.user)
        except ValueError as error:
            detail = {"detail": str(error) or "Invalid YouTube URL."}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        data = QuizWithTimestampsSerializer(quiz).data
        return Response(data, status=status.HTTP_201_CREATED)


class QuizListView(generics.ListAPIView):
    """List all quizzes for the authenticated user."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return quizzes belonging to the current user."""
        user = self.request.user
        return Quiz.objects.filter(user=user).order_by("-created_at")


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a single quiz."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return quiz instance or raise 403/404 as specified."""
        quiz = get_object_or_404(Quiz, pk=self.kwargs.get("pk"))
        if quiz.user != self.request.user:
            msg = "You do not have permission to access this quiz."
            raise PermissionDenied(msg)
        return quiz