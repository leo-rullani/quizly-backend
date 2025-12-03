"""High-level helper functions to build quizzes from YouTube videos."""

from typing import Any, Dict

from quiz_app.models import Quiz, Question
from quiz_app.utils.youtube import download_youtube_audio
from quiz_app.utils.transcription import transcribe_audio
from quiz_app.utils.gemini_client import generate_quiz_from_transcript


def create_quiz_from_youtube_url(url: str, user) -> Quiz:
    """Create and persist a quiz for the given user and YouTube URL."""
    audio_path, canonical_url = download_youtube_audio(url)
    transcript = transcribe_audio(str(audio_path))
    quiz_data = generate_quiz_from_transcript(transcript)
    video_url = str(canonical_url)
    return _create_quiz_with_questions(quiz_data, video_url, user)


def _create_quiz_with_questions(
    quiz_data: Dict[str, Any],
    video_url: str,
    user,
) -> Quiz:
    """Create a Quiz and its Question objects from AI output."""
    quiz = _create_quiz_instance(quiz_data, video_url, user)
    _create_questions_for_quiz(quiz, quiz_data["questions"])
    return quiz


def _create_quiz_instance(
    quiz_data: Dict[str, Any],
    video_url: str,
    user,
) -> Quiz:
    """Create a single Quiz instance."""
    return Quiz.objects.create(
        user=user,
        title=quiz_data["title"],
        description=quiz_data.get("description", ""),
        video_url=video_url,
    )


def _create_questions_for_quiz(quiz: Quiz, questions: list[Dict[str, Any]]) -> None:
    """Create Question objects for the given quiz."""
    Question.objects.bulk_create(
        [
            Question(
                quiz=quiz,
                question_title=item["question_title"],
                question_options=item["question_options"],
                answer=item["answer"],
            )
            for item in questions
        ]
    )