"""
Azure Text Analytics service for sentiment analysis with opinion mining.
Provides enhanced sentiment analysis with fallback capabilities.
"""

import os
import logging
from typing import Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from .base import BaseExternalService, retry_on_failure, ServiceResponse

logger = logging.getLogger(__name__)


class AzureTextAnalyticsService(BaseExternalService):
    """Enhanced Azure Text Analytics service with opinion mining."""
    
    def __init__(self):
        super().__init__("Azure Text Analytics")
        self.endpoint = os.environ.get('AZURE_TEXT_ANALYTICS_ENDPOINT')
        self.key = os.environ.get('AZURE_TEXT_ANALYTICS_KEY')
        self.initialize()
    
    def _validate_credentials(self) -> bool:
        """Validate Azure Text Analytics credentials."""
        return bool(self.endpoint and self.key)
    
    def _initialize_client(self) -> bool:
        """Initialize Azure Text Analytics client."""
        try:
            self.client = TextAnalyticsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.key)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Azure Text Analytics client: {str(e)}")
            return False
    
    @retry_on_failure(max_retries=2, delay=1.0)
    def analyze_sentiment_with_opinions(self, text: str) -> ServiceResponse:
        """
        Analyze sentiment with opinion mining for detailed insights.
        Returns enhanced sentiment data including key phrases and opinions.
        """
        if not self.is_available:
            return self._get_fallback_sentiment(text)
        
        try:
            # Perform sentiment analysis with opinion mining
            documents = [text]
            result = self.client.analyze_sentiment(
                documents, 
                show_opinion_mining=True,
                language="en"
            )
            
            if result and not result[0].is_error:
                doc = result[0]
                
                # Extract key phrases in parallel
                key_phrases_result = self.client.extract_key_phrases(documents, language="en")
                key_phrases = key_phrases_result[0].key_phrases if key_phrases_result and not key_phrases_result[0].is_error else []
                
                # Build comprehensive result
                sentiment_data = self._build_sentiment_data(doc, key_phrases)
                
                logger.info(f"Sentiment analysis completed: {doc.sentiment} ({sentiment_data['confidence_score']:.2f})")
                return ServiceResponse(
                    success=True,
                    data=sentiment_data,
                    service_used="azure_text_analytics"
                )
            else:
                logger.warning("Azure Text Analytics returned error, using fallback")
                return self._get_fallback_sentiment(text)
                
        except Exception as e:
            logger.error(f"Azure Text Analytics error: {str(e)}")
            return self._get_fallback_sentiment(text)
    
    def _build_sentiment_data(self, doc, key_phrases: list) -> Dict[str, Any]:
        """Build comprehensive sentiment data from Azure response."""
        sentiment_data = {
            'sentiment': doc.sentiment,
            'confidence_score': getattr(doc.confidence_scores, doc.sentiment, 0.0),
            'confidence_scores': {
                'positive': doc.confidence_scores.positive,
                'neutral': doc.confidence_scores.neutral,
                'negative': doc.confidence_scores.negative
            },
            'key_phrases': key_phrases[:10],  # Limit to top 10
            'opinions': [],
            'sentences': []
        }
        
        # Extract opinions for aspect-based analysis
        for sentence in doc.sentences:
            sentence_data = {
                'text': sentence.text,
                'sentiment': sentence.sentiment,
                'confidence_score': getattr(sentence.confidence_scores, sentence.sentiment, 0.0)
            }
            sentiment_data['sentences'].append(sentence_data)
            
            # Extract mined opinions
            if hasattr(sentence, 'mined_opinions'):
                for opinion in sentence.mined_opinions:
                    opinion_data = {
                        'target': {
                            'text': opinion.target.text,
                            'sentiment': opinion.target.sentiment,
                            'confidence_score': getattr(opinion.target.confidence_scores, opinion.target.sentiment, 0.0)
                        },
                        'assessments': []
                    }
                    
                    for assessment in opinion.assessments:
                        assessment_data = {
                            'text': assessment.text,
                            'sentiment': assessment.sentiment,
                            'confidence_score': getattr(assessment.confidence_scores, assessment.sentiment, 0.0)
                        }
                        opinion_data['assessments'].append(assessment_data)
                    
                    sentiment_data['opinions'].append(opinion_data)
        
        return sentiment_data
    
    def _get_fallback_sentiment(self, text: str) -> ServiceResponse:
        """Fallback sentiment analysis for demo purposes."""
        # Simple keyword-based fallback
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'worst', 'disappointing']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = 0.8
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = 0.8
        else:
            sentiment = 'neutral'
            confidence = 0.6
        
        fallback_data = {
            'sentiment': sentiment,
            'confidence_score': confidence,
            'confidence_scores': {
                'positive': confidence if sentiment == 'positive' else 0.3,
                'neutral': confidence if sentiment == 'neutral' else 0.3,
                'negative': confidence if sentiment == 'negative' else 0.3
            },
            'key_phrases': [],
            'opinions': [],
            'sentences': [{'text': text, 'sentiment': sentiment, 'confidence_score': confidence}]
        }
        
        return ServiceResponse(
            success=True,
            data=fallback_data,
            service_used="fallback"
        )