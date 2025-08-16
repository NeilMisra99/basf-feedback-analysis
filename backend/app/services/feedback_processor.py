"""
Main feedback processor that orchestrates the complete analysis pipeline.
Coordinates sentiment analysis, response generation, and audio synthesis.
"""

import logging
from typing import Optional
from app import db
from app.models import Feedback, SentimentAnalysis, AIResponse, AudioFile
from .text_analytics import AzureTextAnalyticsService
from .openai_service import OpenAIResponseService
from .speech_service import AzureSpeechService

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """
    Main processor that orchestrates the complete feedback analysis pipeline.
    Implements a clean separation of concerns with proper error handling.
    """
    
    def __init__(self):
        """Initialize all service components."""
        self.text_analytics = AzureTextAnalyticsService()
        self.openai_service = OpenAIResponseService()
        self.speech_service = AzureSpeechService()
    
    def process_feedback_complete(self, feedback_id: str) -> bool:
        """
        Process feedback through the complete enhanced pipeline:
        1. Enhanced sentiment analysis with opinion mining
        2. Context-aware AI response generation
        3. Emotion-based audio synthesis with SSML
        
        Args:
            feedback_id: The ID of the feedback to process
            
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            # Get feedback from database
            feedback = Feedback.query.get(feedback_id)
            if not feedback:
                logger.error(f"Feedback {feedback_id} not found")
                return False
            
            logger.info(f"Starting enhanced processing for feedback {feedback_id}")
            
            # Step 1: Enhanced Sentiment Analysis
            sentiment_result = self._process_sentiment_analysis(feedback)
            if not sentiment_result:
                logger.error(f"Sentiment analysis failed for feedback {feedback_id}")
                return False
            
            # Step 2: Generate Contextual AI Response
            response_result = self._process_ai_response(feedback, sentiment_result.data)
            if not response_result:
                logger.error(f"AI response generation failed for feedback {feedback_id}")
                return False
            
            # Step 3: Generate Emotion-Aware Audio (optional)
            audio_result = self._process_audio_generation(feedback, sentiment_result.data, response_result.data)
            # Audio generation failure is not critical - log but continue
            
            logger.info(f"Enhanced processing completed for feedback {feedback_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in enhanced processing for feedback {feedback_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def _process_sentiment_analysis(self, feedback: Feedback) -> Optional[object]:
        """Process sentiment analysis and save to database."""
        try:
            sentiment_result = self.text_analytics.analyze_sentiment_with_opinions(feedback.text)
            
            if sentiment_result.success and sentiment_result.data:
                # Store enhanced sentiment analysis
                sentiment_analysis = SentimentAnalysis(
                    feedback_id=feedback.id,
                    sentiment=sentiment_result.data['sentiment'],
                    confidence_score=sentiment_result.data['confidence_score']
                )
                db.session.add(sentiment_analysis)
                db.session.commit()
                
                logger.info(f"Sentiment analysis saved: {sentiment_result.data['sentiment']} "
                           f"(confidence: {sentiment_result.data['confidence_score']:.2f}, "
                           f"service: {sentiment_result.service_used})")
                
                return sentiment_result
            else:
                logger.error(f"Sentiment analysis failed: {sentiment_result.error}")
                return None
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            db.session.rollback()
            return None
    
    def _process_ai_response(self, feedback: Feedback, sentiment_data: dict) -> Optional[object]:
        """Process AI response generation and save to database."""
        try:
            response_result = self.openai_service.generate_contextual_response(
                feedback.text, sentiment_data
            )
            
            if response_result.success and response_result.data:
                # Store AI response
                ai_response = AIResponse(
                    feedback_id=feedback.id,
                    response_text=response_result.data['response_text'],
                    model_used=response_result.data['model_used']
                )
                db.session.add(ai_response)
                db.session.commit()
                
                logger.info(f"AI response generated using {response_result.data['model_used']} "
                           f"(service: {response_result.service_used})")
                
                return response_result
            else:
                logger.error(f"AI response generation failed: {response_result.error}")
                return None
                
        except Exception as e:
            logger.error(f"Error in AI response generation: {str(e)}")
            db.session.rollback()
            return None
    
    def _process_audio_generation(self, feedback: Feedback, sentiment_data: dict, response_data: dict) -> Optional[object]:
        """Process audio generation and save to database (optional step)."""
        try:
            audio_result = self.speech_service.generate_emotion_aware_audio(
                response_data['response_text'], sentiment_data, feedback.id
            )
            
            if audio_result.success and audio_result.data:
                # Store audio file metadata with blob information
                audio_data = audio_result.data
                storage_type = 'blob' if audio_data.get('blob_url') else 'local'
                
                audio_file = AudioFile(
                    feedback_id=feedback.id,
                    file_path=audio_data['file_path'],
                    blob_url=audio_data.get('blob_url'),
                    file_size=audio_data.get('file_size', 0),
                    storage_type=storage_type,
                    duration_seconds=self.speech_service.estimate_duration(response_data['response_text'])
                )
                db.session.add(audio_file)
                db.session.commit()
                
                logger.info(f"Emotion-aware audio generated: {audio_result.data['voice_used']} "
                           f"with {audio_result.data['emotion_style']} style")
                
                return audio_result
            else:
                logger.warning(f"Audio generation failed: {audio_result.error if audio_result else 'Unknown error'}")
                return None
                
        except Exception as e:
            logger.warning(f"Error in audio generation (non-critical): {str(e)}")
            # Audio generation is optional - don't rollback the transaction
            return None
    
    def get_service_status(self) -> dict:
        """Get the current status of all services."""
        return {
            'text_analytics': {
                'available': self.text_analytics.is_available,
                'service': self.text_analytics.service_name
            },
            'openai': {
                'available': self.openai_service.is_available,
                'service': self.openai_service.service_name
            },
            'speech': {
                'available': self.speech_service.is_available,
                'service': self.speech_service.service_name
            }
        }