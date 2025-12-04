"""Serializers for quiz creation and quiz management."""

from rest_framework import serializers

from quiz_app.models import Quiz, Question


class CreateQuizSerializer(serializers.Serializer):
    """Validate input for the createQuiz endpoint."""

    url = serializers.URLField(
        help_text="YouTube URL, e.g. https://youtu.be/VIDEO_ID"
    )


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize a question without timestamps (for list/detail responses)."""

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
        ]
        read_only_fields = ["id"]


class QuestionWithTimestampsSerializer(serializers.ModelSerializer):
    """Serialize a question including timestamps (for createQuiz response)."""

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
    """Serialize a quiz with questions, without question timestamps."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "questions"]


class QuizWithTimestampsSerializer(serializers.ModelSerializer):
    """Serialize a quiz where each question includes timestamps."""

    questions = QuestionWithTimestampsSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "questions"]