"""Background processing system for async feedback processing."""

import threading
import logging
from queue import Queue
from typing import Optional
from app import db
from app.models import Feedback
from app.services.feedback_processor import FeedbackProcessor

logger = logging.getLogger(__name__)

def _get_feedback_with_relations(feedback_id):
    """Helper to get feedback with all related data."""
    from sqlalchemy.orm import joinedload
    return Feedback.query.options(
        joinedload(Feedback.sentiment_analysis),
        joinedload(Feedback.ai_response),
        joinedload(Feedback.audio_file)
    ).get(feedback_id)

class BackgroundProcessor:
    
    def __init__(self):
        self.processing_queue = Queue()
        self.feedback_processor = FeedbackProcessor()
        self.worker_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.sse_manager = None
        self.app = None
        
    def set_sse_manager(self, sse_manager):
        """Set the SSE manager for real-time updates."""
        self.sse_manager = sse_manager
        
    def set_app(self, app):
        """Set the Flask app for application context."""
        self.app = app
        
    def start(self):
        """Start the background processing worker."""
        if self.is_running:
            return
            
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Background processor started")
        
    def stop(self):
        """Stop the background processing worker."""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Background processor stopped")
        
    def queue_feedback_processing(self, feedback_id: str):
        """Queue feedback for background processing."""
        self.processing_queue.put(feedback_id)
        logger.info(f"Queued feedback {feedback_id} for processing")
        
    def _worker_loop(self):
        """Main worker loop for processing feedback."""
        while self.is_running:
            try:
                feedback_id = self.processing_queue.get(timeout=1)
                self._process_feedback(feedback_id)
                self.processing_queue.task_done()
            except:
                continue
                
    def _process_feedback(self, feedback_id: str):
        """Process a single feedback item."""
        if not self.app:
            logger.error("No Flask app context available for background processing")
            return
            
        with self.app.app_context():
            try:
                logger.info(f"Starting processing for feedback {feedback_id}")
                success = self.feedback_processor.process_feedback_complete(feedback_id)
                self._update_feedback_status(feedback_id, 'completed' if success else 'failed')
                logger.info(f"Feedback {feedback_id} processing {'completed' if success else 'failed'}")
            except Exception as e:
                logger.error(f"Error processing feedback {feedback_id}: {str(e)}")
                self._update_feedback_status(feedback_id, 'failed')
    
    def _update_feedback_status(self, feedback_id: str, status: str):
        """Update feedback status and send real-time update."""
        try:
            feedback = _get_feedback_with_relations(feedback_id)
            if feedback:
                feedback.processing_status = status
                db.session.commit()
                if self.sse_manager:
                    self.sse_manager.send_feedback_update(feedback)
            else:
                logger.error(f"Feedback {feedback_id} not found in database")
        except Exception as e:
            logger.error(f"Failed to update feedback status: {str(e)}")

# Global instance
background_processor = BackgroundProcessor()