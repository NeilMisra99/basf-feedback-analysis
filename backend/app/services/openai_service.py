"""
OpenAI service for generating contextual responses based on sentiment analysis.
Provides intelligent response generation with fallback capabilities.
"""

import os
import logging
from typing import Dict, Any
from openai import OpenAI
from .base import BaseExternalService, retry_on_failure, ServiceResponse

logger = logging.getLogger(__name__)


class OpenAIResponseService(BaseExternalService):
    """Enhanced OpenAI service for sentiment-aware response generation."""
    
    def __init__(self):
        super().__init__("OpenAI")
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4o')
        self.initialize()
    
    def _validate_credentials(self) -> bool:
        """Validate OpenAI API credentials."""
        return bool(self.api_key)
    
    def _initialize_client(self) -> bool:
        """Initialize OpenAI client."""
        try:
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    @retry_on_failure(max_retries=2, delay=1.0)
    def generate_contextual_response(self, feedback_text: str, sentiment_data: Dict[str, Any]) -> ServiceResponse:
        """
        Generate contextual response based on sentiment analysis and feedback content.
        """
        if not self.is_available:
            return self._get_fallback_response(feedback_text, sentiment_data)
        
        try:
            sentiment = sentiment_data.get('sentiment', 'neutral')
            confidence = sentiment_data.get('confidence_score', 0.5)
            key_phrases = sentiment_data.get('key_phrases', [])
            opinions = sentiment_data.get('opinions', [])
            
            # Build context-aware prompt
            context = self._build_response_context(sentiment, confidence, key_phrases, opinions)
            
            prompt = self._create_prompt(feedback_text, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert customer service representative known for empathetic, personalized responses."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            response_data = {
                'response_text': response_text,
                'model_used': self.model,
                'tokens_used': response.usage.total_tokens,
                'sentiment_addressed': sentiment,
                'key_phrases_used': key_phrases[:3]  # Track which phrases were addressed
            }
            
            return ServiceResponse(
                success=True,
                data=response_data,
                service_used="openai"
            )
            
        except Exception as e:
            logger.error(f"OpenAI response generation error: {str(e)}")
            return self._get_fallback_response(feedback_text, sentiment_data)
    
    def _create_prompt(self, feedback_text: str, context: str) -> str:
        """Create the prompt for response generation."""
        return f"""
        Generate a professional, empathetic customer service response to this feedback.
        
        Customer Feedback: "{feedback_text}"
        
        Analysis Context:
        {context}
        
        Response Requirements:
        1. Be genuine and empathetic
        2. Address the specific sentiment and key points mentioned
        3. Use appropriate tone for the sentiment level
        4. Keep response concise but meaningful (2-3 sentences)
        5. If specific aspects were mentioned, acknowledge them
        6. Provide appropriate next steps or appreciation
        
        Generate only the response text, no additional formatting.
        """
    
    def _build_response_context(self, sentiment: str, confidence: float, key_phrases: list, opinions: list) -> str:
        """Build context string for prompt."""
        context_parts = [
            f"- Overall Sentiment: {sentiment} (confidence: {confidence:.2f})"
        ]
        
        if key_phrases:
            context_parts.append(f"- Key Topics: {', '.join(key_phrases[:5])}")
        
        if opinions:
            opinion_summary = []
            for opinion in opinions[:3]:  # Top 3 opinions
                target = opinion['target']['text']
                assessments = [a['text'] for a in opinion['assessments'][:2]]
                opinion_summary.append(f"{target}: {', '.join(assessments)}")
            context_parts.append(f"- Specific Aspects: {'; '.join(opinion_summary)}")
        
        return '\n'.join(context_parts)
    
    def _get_fallback_response(self, feedback_text: str, sentiment_data: Dict[str, Any]) -> ServiceResponse:
        """Fallback response when OpenAI is not available."""
        sentiment = sentiment_data.get('sentiment', 'neutral')
        
        responses = {
            'positive': "Thank you so much for your wonderful feedback! We're thrilled to hear about your positive experience and truly appreciate you taking the time to share it with us.",
            'negative': "We sincerely appreciate you bringing this to our attention and apologize for any inconvenience you've experienced. Your feedback is invaluable in helping us improve our service.",
            'mixed': "Thank you for your detailed feedback. We appreciate both the positive aspects you've highlighted and the areas for improvement you've identified. This balanced perspective helps us understand how to better serve our customers.",
            'neutral': "Thank you for your feedback. We appreciate you taking the time to share your thoughts with us, and we'll use this information to continue improving our service."
        }
        
        response_data = {
            'response_text': responses.get(sentiment, responses['neutral']),
            'model_used': 'fallback',
            'tokens_used': 0,
            'sentiment_addressed': sentiment,
            'key_phrases_used': []
        }
        
        return ServiceResponse(
            success=True,
            data=response_data,
            service_used="fallback"
        )