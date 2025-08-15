"""
Base service classes providing common functionality for external services.
Implements retry logic, error handling, and service validation patterns.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from functools import wraps
import time

logger = logging.getLogger(__name__)


class BaseExternalService(ABC):
    """
    Abstract base class for external service integrations.
    Provides common patterns for service initialization and validation.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.client = None
        self.is_available = False
        
    @abstractmethod
    def _initialize_client(self) -> bool:
        """Initialize the service client. Return True if successful."""
        pass
    
    @abstractmethod
    def _validate_credentials(self) -> bool:
        """Validate service credentials. Return True if valid."""
        pass
    
    def initialize(self):
        """Initialize and validate the service."""
        try:
            if self._validate_credentials() and self._initialize_client():
                self.is_available = True
                logger.info(f"{self.service_name} service initialized successfully")
            else:
                self.is_available = False
                logger.warning(f"{self.service_name} service not available - using fallback")
        except Exception as e:
            logger.error(f"Failed to initialize {self.service_name} service: {str(e)}")
            self.is_available = False


def retry_on_failure(max_retries: int = 2, delay: float = 1.0):
    """
    Decorator to retry operations on failure with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


class ServiceResponse:
    """Standardized response wrapper for service operations."""
    
    def __init__(self, success: bool, data: Any = None, error: str = None, service_used: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.service_used = service_used
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'service_used': self.service_used,
            'timestamp': self.timestamp
        }