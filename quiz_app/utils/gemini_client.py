from __future__ import annotations

import json
import os
from typing import Any, Dict

from google import genai


GEMINI_MODEL = "gemini-2.5-flash"

PROMPT_TEMPLATE = """
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }
  ]
}

Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in "question_options".
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.
- Generate exactly 10 questions.

Transcript:
""".strip()


def get_gemini_client() -> genai.Client:
    """Create a Gemini client from environment API key."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def build_quiz_prompt(transcript: str) -> str:
    """Append transcript to the static quiz instructions."""
    return f"{PROMPT_TEMPLATE}\n{transcript}"


def strip_markdown_fences(text: str) -> str:
    """Remove ``` and optional 'json' from a response."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("```", 2)
        cleaned = parts[1] if len(parts) > 1 else cleaned
        cleaned = cleaned.lstrip("json").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0].strip()
    return cleaned


def parse_quiz_json(raw: str) -> Dict[str, Any]:
    """Convert cleaned JSON text to a Python dict."""
    cleaned = strip_markdown_fences(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Gemini returned non-JSON output: {exc}") from exc


def generate_quiz_from_transcript(transcript: str) -> Dict[str, Any]:
    """Call Gemini with the transcript and parse quiz JSON."""
    client = get_gemini_client()
    prompt = build_quiz_prompt(transcript)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    text = response.text or ""
    return parse_quiz_json(text)