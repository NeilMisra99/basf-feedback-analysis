from app import db
from datetime import datetime
from sqlalchemy import Index
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), index=True)  # Add index for filtering
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Add index for sorting
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optimized relationships with lazy loading control
    sentiment_analysis = db.relationship('SentimentAnalysis', backref='feedback', uselist=False, lazy='select')
    ai_response = db.relationship('AIResponse', backref='feedback', uselist=False, lazy='select')
    audio_file = db.relationship('AudioFile', backref='feedback', uselist=False, lazy='select')
    
    # Composite index for common query patterns
    __table_args__ = (
        Index('idx_feedback_created_category', 'created_at', 'category'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class SentimentAnalysis(db.Model):
    __tablename__ = 'sentiment_analysis'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    feedback_id = db.Column(db.String(36), db.ForeignKey('feedback.id'), nullable=False, unique=True)  # Ensure one-to-one
    sentiment = db.Column(db.String(20), nullable=False, index=True)  # Add index for grouping
    confidence_score = db.Column(db.Float)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
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
    feedback_id = db.Column(db.String(36), db.ForeignKey('feedback.id'), nullable=False, unique=True)  # Ensure one-to-one
    response_text = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(50), index=True)  # Add index for analytics
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
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
    feedback_id = db.Column(db.String(36), db.ForeignKey('feedback.id'), nullable=False, unique=True)  # Ensure one-to-one
    file_path = db.Column(db.String(255), nullable=False, unique=True)  # Prevent duplicate files
    duration_seconds = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'feedback_id': self.feedback_id,
            'file_path': self.file_path,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }