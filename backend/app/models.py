from app import db
from datetime import datetime, timezone
from sqlalchemy import Index
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), index=True)  # Add index for filtering
    processing_status = db.Column(db.String(20), default='processing', index=True)  # processing, completed, failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Add index for sorting
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Optimized relationships with lazy loading control
    sentiment_analysis = db.relationship('SentimentAnalysis', backref='feedback', uselist=False, lazy='select')
    ai_response = db.relationship('AIResponse', backref='feedback', uselist=False, lazy='select')
    audio_file = db.relationship('AudioFile', backref='feedback', uselist=False, lazy='select')
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_feedback_created_category', 'created_at', 'category'),
        Index('idx_feedback_status_created', 'processing_status', 'created_at'),  # For filtering by status and sorting
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'category': self.category,
            'processing_status': self.processing_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class SentimentAnalysis(db.Model):
    __tablename__ = 'sentiment_analysis'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    feedback_id = db.Column(db.String(36), db.ForeignKey('feedback.id'), nullable=False, unique=True, index=True)  # Index for JOINs
    sentiment = db.Column(db.String(20), nullable=False, index=True)  # Add index for grouping
    confidence_score = db.Column(db.Float)
    processed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Composite index for dashboard query optimization
    __table_args__ = (
        Index('idx_sentiment_feedback_sentiment', 'feedback_id', 'sentiment'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'feedback_id': self.feedback_id,
            'sentiment': self.sentiment,
            'confidence_score': self.confidence_score,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
        }

class AIResponse(db.Model):
    __tablename__ = 'ai_responses'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    feedback_id = db.Column(db.String(36), db.ForeignKey('feedback.id'), nullable=False, unique=True, index=True)  # Index for JOINs
    response_text = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(50), index=True)  # Add index for analytics
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'feedback_id': self.feedback_id,
            'response_text': self.response_text,
            'model_used': self.model_used,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
        }

class AudioFile(db.Model):
    __tablename__ = 'audio_files'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    feedback_id = db.Column(db.String(36), db.ForeignKey('feedback.id'), nullable=False, unique=True, index=True)  # Index for JOINs
    file_path = db.Column(db.String(255), nullable=False, unique=True)  # Local path or blob name
    blob_url = db.Column(db.String(500), nullable=True)  # Blob Storage URL
    duration_seconds = db.Column(db.Float)
    file_size = db.Column(db.Integer, nullable=True)  # File size in bytes
    storage_type = db.Column(db.String(20), default='local')  # 'local' or 'blob'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'feedback_id': self.feedback_id,
            'file_path': self.file_path,
            'blob_url': self.blob_url,
            'duration_seconds': self.duration_seconds,
            'file_size': self.file_size,
            'storage_type': self.storage_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }