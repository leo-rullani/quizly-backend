from rest_framework import serializers


class CreateQuizSerializer(serializers.Serializer):
    """Serializer for createQuiz endpoint input."""
    url = serializers.URLField(
        help_text="Any valid YouTube URL, e.g. https://youtu.be/VIDEO_ID"
    )