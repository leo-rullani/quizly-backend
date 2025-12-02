from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from quiz_app.utils.youtube import download_youtube_audio
from quiz_app.utils.transcription import transcribe_audio
from quiz_app.utils.gemini_client import generate_quiz_from_transcript

from rest_framework.parsers import JSONParser
from .parsers import PlainTextJSONParser

class CreateQuizView(APIView):
    """Handle quiz creation from a YouTube URL."""
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, PlainTextJSONParser]

    def post(self, request):
        """
        Download audio, transcribe it and return meta data.
        """
        url = request.data.get("url")
        if not url:
            return Response(
                {"detail": "URL is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            audio_path, canonical_url = download_youtube_audio(url)
            transcript = transcribe_audio(str(audio_path))
            quiz = generate_quiz_from_transcript(transcript)
        except ValueError:
            return Response(
                {"detail": "Invalid YouTube URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {
            "video_url": str(canonical_url),
            "audio_file": str(audio_path),
            "transcript": transcript,
            "quiz": quiz,
        }
        return Response(data, status=status.HTTP_201_CREATED)