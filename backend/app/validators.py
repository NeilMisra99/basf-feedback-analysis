"""
Input validation utilities for the feedback analysis application.
Provides comprehensive validation with clear error messages.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from functools import wraps
from flask import request, jsonify


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)


class FeedbackValidator:
    """Validator for feedback-related input data."""
    
    # Configuration constants
    MIN_TEXT_LENGTH = 10
    MAX_TEXT_LENGTH = 5000
    VALID_CATEGORIES = ['general', 'service', 'product', 'support', 'billing', 'technical']
    
    @classmethod
    def validate_feedback_submission(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate feedback submission data.
        
        Args:
            data: Request data dictionary
            
        Returns:
            Dict with validated and sanitized data
            
        Raises:
            ValidationError: If validation fails
        """
        if not data:
            raise ValidationError("Request body is required", code="MISSING_BODY")
        
        # Validate text field
        text = cls._validate_text(data.get('text'))
        
        # Validate category (optional)
        category = cls._validate_category(data.get('category', 'general'))
        
        return {
            'text': text,
            'category': category
        }
    
    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate feedback text content."""
        if not text:
            raise ValidationError("Feedback text is required", field="text", code="MISSING_TEXT")
        
        if not isinstance(text, str):
            raise ValidationError("Feedback text must be a string", field="text", code="INVALID_TYPE")
        
        # Clean and validate text
        text = text.strip()
        
        if len(text) < cls.MIN_TEXT_LENGTH:
            raise ValidationError(
                f"Feedback text must be at least {cls.MIN_TEXT_LENGTH} characters",
                field="text",
                code="TEXT_TOO_SHORT"
            )
        
        if len(text) > cls.MAX_TEXT_LENGTH:
            raise ValidationError(
                f"Feedback text must not exceed {cls.MAX_TEXT_LENGTH} characters",
                field="text", 
                code="TEXT_TOO_LONG"
            )
        
        # Check for potentially malicious content
        if cls._contains_suspicious_content(text):
            raise ValidationError(
                "Feedback contains inappropriate content",
                field="text",
                code="SUSPICIOUS_CONTENT"
            )
        
        return text
    
    @classmethod
    def _validate_category(cls, category: Any) -> str:
        """Validate feedback category."""
        if category is None:
            return 'general'
        
        if not isinstance(category, str):
            raise ValidationError("Category must be a string", field="category", code="INVALID_TYPE")
        
        category = category.strip().lower()
        
        if category not in cls.VALID_CATEGORIES:
            raise ValidationError(
                f"Category must be one of: {', '.join(cls.VALID_CATEGORIES)}",
                field="category",
                code="INVALID_CATEGORY"
            )
        
        return category
    
    @classmethod
    def _contains_suspicious_content(cls, text: str) -> bool:
        """Check for potentially malicious or inappropriate content."""
        # Basic patterns for suspicious content
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'data:.*base64',  # Base64 data URLs
            r'<iframe[^>]*>',  # Iframe tags
            r'<object[^>]*>',  # Object tags
            r'<embed[^>]*>',  # Embed tags
        ]
        
        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
                return True
        
        return False


class QueryValidator:
    """Validator for query parameters."""
    
    @classmethod
    def validate_pagination(cls, page: Any, per_page: Any) -> Tuple[int, int]:
        """
        Validate pagination parameters.
        
        Returns:
            Tuple of (page, per_page) with validated values
        """
        # Validate page
        try:
            page = int(page) if page is not None else 1
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        # Validate per_page
        try:
            per_page = int(per_page) if per_page is not None else 10
            per_page = max(1, min(per_page, 100))  # Clamp between 1 and 100
        except (ValueError, TypeError):
            per_page = 10
        
        return page, per_page
    
    @classmethod
    def validate_category_filter(cls, category: Any) -> Optional[str]:
        """Validate category filter parameter."""
        if not category:
            return None
        
        if not isinstance(category, str):
            return None
        
        category = category.strip().lower()
        return category if category in FeedbackValidator.VALID_CATEGORIES else None


def validate_json_request(validator_func):
    """
    Decorator to validate JSON request data using a validator function.
    
    Args:
        validator_func: Function that takes request data and returns validated data
    """
    def decorator(route_func):
        @wraps(route_func)
        def wrapper(*args, **kwargs):
            try:
                # Check content type
                if not request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Content-Type must be application/json',
                        'code': 'INVALID_CONTENT_TYPE'
                    }), 400
                
                # Get JSON data
                data = request.get_json(silent=True)
                
                # Validate data
                validated_data = validator_func(data)
                
                # Store validated data for the route
                request.validated_data = validated_data
                
                return route_func(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    'status': 'error',
                    'message': e.message,
                    'field': e.field,
                    'code': e.code
                }), 400
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid request data',
                    'code': 'VALIDATION_ERROR'
                }), 400
        
        return wrapper
    return decorator


def handle_database_errors(func):
    """Decorator to handle common database errors gracefully."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the full error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            
            # Return a generic error response
            return jsonify({
                'status': 'error',
                'message': 'A database error occurred. Please try again.',
                'code': 'DATABASE_ERROR'
            }), 500
    
    return wrapper