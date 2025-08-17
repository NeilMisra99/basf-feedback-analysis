"""Shared query helpers to avoid duplication."""

from sqlalchemy.orm import joinedload
from app.models import Feedback


def get_feedback_with_relations(feedback_id: str):
    """Fetch single feedback with all related entities eagerly loaded."""
    return (
        Feedback.query.options(
            joinedload(Feedback.sentiment_analysis),
            joinedload(Feedback.ai_response),
            joinedload(Feedback.audio_file),
        ).get(feedback_id)
    )


def base_feedback_query():
    """Base query with eager loaded relations for listing/filtering."""
    return Feedback.query.options(
        joinedload(Feedback.sentiment_analysis),
        joinedload(Feedback.ai_response),
        joinedload(Feedback.audio_file),
    )


