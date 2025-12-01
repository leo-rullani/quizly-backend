from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from quiz_app.utils.youtube import download_youtube_audio


class CreateQuizView(APIView):
    """Handle quiz creation from a YouTube URL."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Download audio and return basic info for now."""
        url = request.data.get("url")
        if not url:
            return Response({"detail": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            audio_path, canonical_url = download_youtube_audio(url)
        except ValueError:
            return Response({"detail": "Invalid YouTube URL."}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            "video_url": str(canonical_url),
            "audio_file": str(audio_path),
        }
        return Response(data, status=status.HTTP_201_CREATED)