"""Application configuration."""

import os
from typing import Dict, Any

class Config:
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///feedback_analysis.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'check_same_thread': False} if 'sqlite' in SQLALCHEMY_DATABASE_URI else {}
    }
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    AZURE_TEXT_ANALYTICS_ENDPOINT = os.environ.get('AZURE_TEXT_ANALYTICS_ENDPOINT')
    AZURE_TEXT_ANALYTICS_KEY = os.environ.get('AZURE_TEXT_ANALYTICS_KEY')
    AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
    AZURE_SPEECH_REGION = os.environ.get('AZURE_SPEECH_REGION')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    AUDIO_FILES_DIR = '/tmp'
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate critical configuration and return status (non-throwing)."""
        validation_results = {
            'secret_key': bool(cls.SECRET_KEY),
            'database_configured': bool(cls.SQLALCHEMY_DATABASE_URI),
            'azure_text_analytics': bool(cls.AZURE_TEXT_ANALYTICS_ENDPOINT and cls.AZURE_TEXT_ANALYTICS_KEY),
            'azure_speech': bool(cls.AZURE_SPEECH_KEY and cls.AZURE_SPEECH_REGION),
            'openai': bool(cls.OPENAI_API_KEY),
        }
        return validation_results


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


def get_config() -> Config:
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.environ.get('FLASK_ENV', 'production')
    return config_by_name.get(env, ProductionConfig)