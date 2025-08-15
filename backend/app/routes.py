from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.orm import joinedload
from app import db
from app.models import Feedback, SentimentAnalysis, AIResponse, AudioFile
from app.services import FeedbackProcessor
from app.validators import (
    FeedbackValidator, QueryValidator, ValidationError,
    validate_json_request, handle_database_errors
)
import os
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

def _build_complete_feedback_data(feedback):
    """Build complete feedback data including all related AI data for dashboard"""
    response_data = feedback.to_dict()
    
    if feedback.sentiment_analysis:
        response_data['sentiment_analysis'] = feedback.sentiment_analysis.to_dict()
    
    if feedback.ai_response:
        response_data['ai_response'] = feedback.ai_response.to_dict()
    
    if feedback.audio_file:
        response_data['audio_file'] = feedback.audio_file.to_dict()
        response_data['audio_url'] = f'/api/v1/audio/{feedback.audio_file.id}'
    
    return response_data

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with service status information."""
    try:
        # Test database connectivity
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'unhealthy'
    
    # Get service status
    try:
        processor = FeedbackProcessor()
        services_status = processor.get_service_status()
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
        
        # Process feedback through enhanced pipeline (async-like approach)
        try:
            processor = FeedbackProcessor()
            success = processor.process_feedback_complete(feedback.id)
            
            if not success:
                logger.warning(f"Processing failed for feedback {feedback.id}, but feedback was saved")
        except Exception as e:
            logger.error(f"Processing error for feedback {feedback.id}: {str(e)}")
            # Don't fail the request if processing fails
        
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
        # Validate feedback_id format (basic UUID validation)
        if not feedback_id or len(feedback_id) != 36:
            return jsonify({
                'status': 'error',
                'message': 'Invalid feedback ID format',
                'code': 'INVALID_ID'
            }), 400
        
        # Use eager loading to prevent N+1 queries
        feedback = Feedback.query.options(
            joinedload(Feedback.sentiment_analysis),
            joinedload(Feedback.ai_response),
            joinedload(Feedback.audio_file)
        ).get(feedback_id)
        
        if not feedback:
            return jsonify({
                'status': 'error',
                'message': 'Feedback not found',
                'code': 'NOT_FOUND'
            }), 404
        
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
        query = Feedback.query.options(
            joinedload(Feedback.sentiment_analysis),
            joinedload(Feedback.ai_response),
            joinedload(Feedback.audio_file)
        )
        
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
    """Serve audio files with proper validation and security."""
    try:
        # Validate audio_id format
        if not audio_id or len(audio_id) != 36:
            return jsonify({
                'status': 'error',
                'message': 'Invalid audio ID format',
                'code': 'INVALID_ID'
            }), 400
        
        audio_file = AudioFile.query.get(audio_id)
        
        if not audio_file:
            return jsonify({
                'status': 'error',
                'message': 'Audio file not found',
                'code': 'NOT_FOUND'
            }), 404
        
        # Validate file existence and security
        if not os.path.exists(audio_file.file_path):
            logger.error(f"Audio file missing from disk: {audio_file.file_path}")
            return jsonify({
                'status': 'error',
                'message': 'Audio file not available',
                'code': 'FILE_MISSING'
            }), 404
        
        # Security check: ensure file is within expected directory
        audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'audio_files'))
        file_path = os.path.abspath(audio_file.file_path)
        
        if not file_path.startswith(audio_dir):
            logger.warning(f"Security violation: attempted access to {file_path}")
            return jsonify({
                'status': 'error',
                'message': 'Access denied',
                'code': 'ACCESS_DENIED'
            }), 403
        
        download = request.args.get('download', 'false').lower() == 'true'
        
        return send_file(
            audio_file.file_path,
            as_attachment=download,
            mimetype='audio/mpeg',
            download_name=f'feedback_{audio_file.feedback_id}_response.mp3' if download else None
        )
        
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
        # Use efficient queries for dashboard stats
        total_feedback = Feedback.query.count()
        
        # Optimized sentiment breakdown with single query
        sentiment_stats = db.session.query(
            SentimentAnalysis.sentiment,
            db.func.count(SentimentAnalysis.id)
        ).group_by(SentimentAnalysis.sentiment).all()
        
        sentiment_breakdown = {sentiment: count for sentiment, count in sentiment_stats}
        
        # Get recent feedback with eager loading
        recent_feedback = Feedback.query.options(
            joinedload(Feedback.sentiment_analysis),
            joinedload(Feedback.ai_response),
            joinedload(Feedback.audio_file)
        ).order_by(Feedback.created_at.desc()).limit(5).all()
        
        # Category breakdown for additional insights
        category_stats = db.session.query(
            Feedback.category,
            db.func.count(Feedback.id)
        ).group_by(Feedback.category).all()
        
        category_breakdown = {category or 'uncategorized': count for category, count in category_stats}
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_feedback': total_feedback,
                'sentiment_breakdown': sentiment_breakdown,
                'category_breakdown': category_breakdown,
                'recent_feedback': [
                    _build_complete_feedback_data(feedback)
                    for feedback in recent_feedback
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve dashboard stats: {str(e)}'
        }), 500