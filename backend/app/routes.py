from flask import Blueprint, request, jsonify, send_file, Response, stream_with_context
from app import db
from app.models import Feedback, AudioFile
from app.validators import (
    FeedbackValidator, QueryValidator, ValidationError,
    validate_json_request, handle_database_errors
)
from app.background_processor import background_processor
from app.sse_manager import sse_manager
from app.queries import base_feedback_query, get_feedback_with_relations
import os
import logging
import json
import time
import re
from datetime import timezone
import uuid
from sqlalchemy import text
from app.serializers import serialize_feedback

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

def _is_valid_uuid(uuid_string: str) -> bool:
    """Validate UUID format robustly using uuid module."""
    try:
        uuid.UUID(uuid_string)
        return True
    except Exception:
        return False

def _error_response(message, code, status=400):
    """Create standardized error response."""
    return jsonify({
        'status': 'error',
        'message': message,
        'code': code
    }), status

def _get_feedback_with_relations(feedback_id=None):
    """Deprecated: use helpers in app.queries instead."""
    if feedback_id:
        return get_feedback_with_relations(feedback_id)
    return base_feedback_query()

def _build_complete_feedback_data(feedback):
    """Deprecated: use serialize_feedback instead."""
    return serialize_feedback(feedback)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with service status information."""
    try:
        # Test database connectivity
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'unhealthy'
    
    # Get service status
    try:
        # Avoid heavy client instantiation: check presence of env/config only
        services_status = {
            'text_analytics': {'available': bool(os.environ.get('AZURE_TEXT_ANALYTICS_ENDPOINT') and os.environ.get('AZURE_TEXT_ANALYTICS_KEY')), 'service': 'Azure Text Analytics'},
            'openai': {'available': bool(os.environ.get('OPENAI_API_KEY')), 'service': 'OpenAI'},
            'speech': {'available': bool(os.environ.get('AZURE_SPEECH_KEY') and os.environ.get('AZURE_SPEECH_REGION')), 'service': 'Azure Speech'}
        }
    except Exception as e:
        logger.error(f"Service status check failed: {str(e)}")
        services_status = {'error': 'Unable to check service status'}
    
    response_data = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'message': 'Feedback Analysis API is running',
        'database': db_status,
        'services': services_status,
        'version': '1.0.0'
    }
    
    status_code = 200 if db_status == 'healthy' else 503
    return jsonify(response_data), status_code

@api_bp.route('/feedback', methods=['POST'])
@validate_json_request(FeedbackValidator.validate_feedback_submission)
@handle_database_errors
def submit_feedback():
    """Submit new feedback with comprehensive validation."""
    try:
        # Get validated data from the decorator
        validated_data = request.validated_data
        
        # Create feedback record
        feedback = Feedback(
            text=validated_data['text'],
            category=validated_data['category']
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        logger.info(f"Feedback {feedback.id} created successfully")
        
        # Immediately set status to processing and notify clients
        feedback.processing_status = 'processing'
        db.session.commit()
        sse_manager.send_feedback_update(feedback)
        
        # Queue feedback for background processing
        background_processor.queue_feedback_processing(feedback.id)
        
        return jsonify({
            'status': 'success',
            'data': feedback.to_dict(),
            'message': 'Feedback submitted successfully'
        }), 201
        
    except ValidationError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': e.message,
            'field': e.field,
            'code': e.code
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in submit_feedback: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit feedback. Please try again.',
            'code': 'SUBMISSION_ERROR'
        }), 500

@api_bp.route('/feedback/<feedback_id>', methods=['GET'])
@handle_database_errors
def get_feedback(feedback_id):
    """Get a specific feedback record with all related data."""
    try:
        # Validate UUID format
        if not _is_valid_uuid(feedback_id):
            return _error_response('Invalid feedback ID format', 'INVALID_ID')
        
        feedback = get_feedback_with_relations(feedback_id)
        
        if not feedback:
            return _error_response('Feedback not found', 'NOT_FOUND', 404)
        
        # Build complete response with all related data
        response_data = _build_complete_feedback_data(feedback)
        
        return jsonify({
            'status': 'success',
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"Error retrieving feedback {feedback_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve feedback',
            'code': 'RETRIEVAL_ERROR'
        }), 500

@api_bp.route('/feedback', methods=['GET'])
@handle_database_errors
def list_feedback():
    """List feedback with pagination and filtering support."""
    try:
        # Validate query parameters
        page, per_page = QueryValidator.validate_pagination(
            request.args.get('page'),
            request.args.get('per_page')
        )
        
        category = QueryValidator.validate_category_filter(
            request.args.get('category')
        )
        
        # Build query with filters and eager loading
        query = base_feedback_query()
        
        # Add category filter if provided and valid
        if category:
            query = query.filter(Feedback.category == category)
        
        # Order by creation date for consistent results
        query = query.order_by(Feedback.created_at.desc())
        
        try:
            feedbacks = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
        except Exception as e:
            logger.error(f"Pagination error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid pagination parameters',
                'code': 'PAGINATION_ERROR'
            }), 400
        
        return jsonify({
            'status': 'success',
            'data': [_build_complete_feedback_data(feedback) for feedback in feedbacks.items],
            'pagination': {
                'page': page,
                'pages': feedbacks.pages,
                'per_page': per_page,
                'total': feedbacks.total,
                'has_next': feedbacks.has_next,
                'has_prev': feedbacks.has_prev
            },
            'filters': {
                'category': category
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve feedback list: {str(e)}'
        }), 500

@api_bp.route('/audio/<audio_id>', methods=['GET'])
@handle_database_errors
def get_audio(audio_id):
    """Serve audio files from Blob Storage or local disk. No regeneration on GET."""
    try:
        if not _is_valid_uuid(audio_id):
            return _error_response('Invalid audio ID format', 'INVALID_ID')

        audio_file = AudioFile.query.get(audio_id)
        if not audio_file:
            return _error_response('Audio file not found', 'NOT_FOUND', 404)

        download = request.args.get('download', 'false').lower() == 'true'
        filename = f'feedback_{audio_file.feedback_id}_response.mp3'

        # Prefer Blob Storage
        from app.services.blob_storage import get_blob_storage
        blob_service = get_blob_storage()
        if blob_service.is_available:
            blob_result = blob_service.get_blob_content(audio_file.feedback_id)
            if blob_result.success and blob_result.data:
                return Response(
                    blob_result.data,
                    mimetype='audio/mpeg',
                    headers={
                        'Content-Length': str(len(blob_result.data)),
                        'Content-Disposition': f'{"attachment" if download else "inline"}; filename="{filename}"'
                    }
                )

        # Fallback to local file
        if os.path.exists(audio_file.file_path):
            return send_file(
                audio_file.file_path,
                as_attachment=download,
                mimetype='audio/mpeg',
                download_name=filename if download else None
            )

        return _error_response('Audio file not available - please try again later', 'FILE_NOT_AVAILABLE', 404)

    except Exception as e:
        logger.error(f"Error serving audio file {audio_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve audio file',
            'code': 'AUDIO_ERROR'
        }), 500

@api_bp.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    try:
        return jsonify({
            'status': 'success',
            'data': _get_dashboard_stats()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve dashboard stats: {str(e)}'
        }), 500


def _get_dashboard_stats():
    """Compose dashboard stats from optimized SQL queries."""
    # Total feedback
    total_feedback = db.session.execute(
        text("SELECT COUNT(*) as count FROM feedback")
    ).scalar() or 0

    # Sentiment breakdown for completed items
    sentiment_results = db.session.execute(
        text(
            """
            SELECT s.sentiment, COUNT(*) as count
            FROM sentiment_analysis s
            JOIN feedback f ON f.id = s.feedback_id
            WHERE f.processing_status = 'completed'
            GROUP BY s.sentiment
            """
        )
    ).fetchall()
    sentiment_breakdown = {row.sentiment: row.count for row in sentiment_results}

    # Category breakdown
    category_results = db.session.execute(
        text(
            """
            SELECT COALESCE(category, 'uncategorized') as category, COUNT(*) as count
            FROM feedback
            GROUP BY category
            """
        )
    ).fetchall()
    category_breakdown = {row.category: row.count for row in category_results}

    # Recent feedback minimal view (limit 5)
    recent_results = db.session.execute(
        text(
            """
            SELECT 
                f.id, f.text, f.category, f.created_at, f.processing_status,
                s.sentiment, s.confidence_score,
                a.response_text,
                af.id as audio_file_id
            FROM feedback f
            LEFT JOIN sentiment_analysis s ON f.id = s.feedback_id
            LEFT JOIN ai_responses a ON f.id = a.feedback_id
            LEFT JOIN audio_files af ON f.id = af.feedback_id
            ORDER BY f.created_at DESC
            LIMIT 5
            """
        )
    ).fetchall()

    recent_feedback_data = []
    for row in recent_results:
        created_at_iso = None
        if row.created_at:
            created_at_iso = (
                row.created_at.replace(tzinfo=timezone.utc).isoformat()
                if hasattr(row.created_at, 'isoformat')
                else str(row.created_at)
            )

        recent_feedback_data.append(
            {
                'id': row.id,
                'text': row.text,
                'category': row.category,
                'created_at': created_at_iso,
                'processing_status': row.processing_status,
                'sentiment_analysis': (
                    {
                        'sentiment': row.sentiment,
                        'confidence_score': row.confidence_score,
                    }
                    if row.sentiment
                    else None
                ),
                'ai_response': (
                    {'response_text': row.response_text} if row.response_text else None
                ),
                'audio_file': ({'id': row.audio_file_id} if row.audio_file_id else None),
                'audio_url': (
                    f'/api/v1/audio/{row.audio_file_id}' if row.audio_file_id else None
                ),
            }
        )

    return {
        'total_feedback': total_feedback,
        'sentiment_breakdown': sentiment_breakdown,
        'category_breakdown': category_breakdown,
        'recent_feedback': recent_feedback_data,
    }

@api_bp.route('/events', methods=['GET'])
def sse_stream():
    """Server-Sent Events endpoint for real-time updates."""
    client = sse_manager.add_client()
    
    def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE connection established'})}\n\n"
            for event in client.get_events():
                yield event
        except Exception as e:
            logger.error(f"SSE stream error: {str(e)}")
            client.disconnect()
    
    return Response(
        stream_with_context(event_generator()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Disable Nginx buffering
            'Content-Type': 'text/event-stream; charset=utf-8',
        }
    )