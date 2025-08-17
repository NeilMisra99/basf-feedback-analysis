"""OpenAI service for generating contextual responses (HTTP API)."""

import os
import logging
from typing import Dict, Any
import requests
from .base import BaseExternalService, retry_on_failure, ServiceResponse

logger = logging.getLogger(__name__)


class OpenAIResponseService(BaseExternalService):
    
    def __init__(self):
        super().__init__("OpenAI")
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4o')
        self.base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com')
        self.timeout_seconds = 30
        self.initialize()
    
    def _validate_credentials(self) -> bool:
        """Validate OpenAI API credentials."""
        return bool(self.api_key)
    
    def _initialize_client(self) -> bool:
        """Validate OpenAI API credentials."""
        return bool(self.base_url and self.api_key)
    
    @retry_on_failure(max_retries=2, delay=1.0)
    def generate_contextual_response(self, feedback_text: str, sentiment_data: Dict[str, Any]) -> ServiceResponse:
        """Generate contextual response using OpenAI Chat Completions API."""
        if not self.is_available:
            return self._get_fallback_response(feedback_text, sentiment_data)
        
        try:
            sentiment = sentiment_data.get('sentiment', 'neutral')
            confidence = sentiment_data.get('confidence_score', 0.5)
            key_phrases = sentiment_data.get('key_phrases', [])
            opinions = sentiment_data.get('opinions', [])
            
            context = self._build_response_context(sentiment, confidence, key_phrases, opinions)
            prompt = self._create_prompt(feedback_text, context)

            url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert customer service representative known for empathetic, personalized responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 200,
                "temperature": 0.7,
            }

            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)
            resp.raise_for_status()
            data = resp.json()

            choices = data.get("choices", [])
            if not choices:
                raise ValueError("OpenAI API returned no choices")

            message = choices[0].get("message", {})
            response_text = (message.get("content") or "").strip()

            usage = data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)

            response_data = {
                'response_text': response_text,
                'model_used': self.model,
                'tokens_used': total_tokens,
                'sentiment_addressed': sentiment,
                'key_phrases_used': key_phrases[:3],
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
            for opinion in opinions[:3]:
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