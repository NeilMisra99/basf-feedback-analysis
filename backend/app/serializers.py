"""Serialization helpers for API and SSE payloads."""

from typing import Dict, Any
from app.models import Feedback


def serialize_feedback(feedback: Feedback) -> Dict[str, Any]:
    """Serialize a `Feedback` model including related entities."""
    data: Dict[str, Any] = feedback.to_dict()

    if getattr(feedback, "sentiment_analysis", None):
        data["sentiment_analysis"] = feedback.sentiment_analysis.to_dict()

    if getattr(feedback, "ai_response", None):
        data["ai_response"] = feedback.ai_response.to_dict()

    if getattr(feedback, "audio_file", None):
        data["audio_file"] = feedback.audio_file.to_dict()
        data["audio_url"] = f"/api/v1/audio/{feedback.audio_file.id}"

    return data


