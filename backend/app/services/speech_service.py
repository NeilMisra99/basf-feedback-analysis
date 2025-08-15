"""
Azure Speech service for generating emotion-aware audio responses.
Provides SSML-based audio synthesis with emotional expression.
"""

import os
import logging
from typing import Dict, Any, Optional
import azure.cognitiveservices.speech as speechsdk
from .base import BaseExternalService, retry_on_failure, ServiceResponse

logger = logging.getLogger(__name__)


class AzureSpeechService(BaseExternalService):
    """Enhanced Azure Speech service with SSML emotion adaptation."""
    
    def __init__(self):
        super().__init__("Azure Speech")
        self.speech_key = os.environ.get('AZURE_SPEECH_KEY')
        self.speech_region = os.environ.get('AZURE_SPEECH_REGION')
        self.initialize()
    
    def _validate_credentials(self) -> bool:
        """Validate Azure Speech credentials."""
        return bool(self.speech_key and self.speech_region)
    
    def _initialize_client(self) -> bool:
        """Initialize Azure Speech configuration."""
        try:
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )
            # Set default voice
            self.speech_config.speech_synthesis_voice_name = "en-US-JennyMultilingualNeural"
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech client: {str(e)}")
            return False
    
    @retry_on_failure(max_retries=1, delay=2.0)  # Lower retries for audio generation
    def generate_emotion_aware_audio(self, text: str, sentiment_data: Dict[str, Any], feedback_id: str) -> ServiceResponse:
        """
        Generate audio with emotion-based voice and SSML styling.
        """
        if not self.is_available:
            logger.info("Speech synthesis skipped - credentials not available")
            return ServiceResponse(
                success=False,
                error="Speech service not available",
                service_used="none"
            )
        
        try:
            sentiment = sentiment_data.get('sentiment', 'neutral')
            confidence = sentiment_data.get('confidence_score', 0.5)
            
            # Create SSML with emotion adaptation
            ssml = self._create_emotion_ssml(text, sentiment, confidence)
            
            # Create audio file path
            audio_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'audio_files')
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, f'{feedback_id}.mp3')
            
            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Generate audio using SSML
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Get audio file size
                file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
                
                logger.info(f"Audio generated successfully: {audio_path} ({file_size} bytes)")
                
                audio_data = {
                    'file_path': audio_path,
                    'file_size': file_size,
                    'voice_used': self._get_voice_for_sentiment(sentiment, confidence),
                    'emotion_style': self._get_emotion_style(sentiment, confidence),
                    'ssml_used': True
                }
                
                return ServiceResponse(
                    success=True,
                    data=audio_data,
                    service_used="azure_speech"
                )
            else:
                logger.error(f"Speech synthesis failed: {result.reason}")
                return ServiceResponse(
                    success=False,
                    error=f"Speech synthesis failed: {result.reason}",
                    service_used="azure_speech"
                )
                
        except Exception as e:
            logger.error(f"Azure speech synthesis error: {str(e)}")
            return ServiceResponse(
                success=False,
                error=str(e),
                service_used="azure_speech"
            )
    
    def _create_emotion_ssml(self, text: str, sentiment: str, confidence: float) -> str:
        """Create SSML with emotion-based styling."""
        voice = self._get_voice_for_sentiment(sentiment, confidence)
        style = self._get_emotion_style(sentiment, confidence)
        style_degree = self._get_style_degree(confidence)
        
        # Build SSML with emotion expression
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice}">
                <mstts:express-as style="{style}" styledegree="{style_degree}">
                    <prosody rate="medium" pitch="medium">
                        {self._escape_ssml_text(text)}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """
        
        return ssml.strip()
    
    def _get_voice_for_sentiment(self, sentiment: str, confidence: float) -> str:
        """Select appropriate voice based on sentiment."""
        voice_mapping = {
            'positive': 'en-US-JennyMultilingualNeural',  # Warm, friendly
            'negative': 'en-US-RyanMultilingualNeural',   # Professional, empathetic
            'neutral': 'en-US-AvaMultilingualNeural'      # Balanced, professional
        }
        return voice_mapping.get(sentiment, voice_mapping['neutral'])
    
    def _get_emotion_style(self, sentiment: str, confidence: float) -> str:
        """Get emotion style based on sentiment and confidence."""
        if sentiment == 'positive':
            return 'cheerful' if confidence > 0.7 else 'friendly'
        elif sentiment == 'negative':
            return 'empathetic' if confidence > 0.7 else 'calm'
        else:
            return 'assistant'  # Professional default
    
    def _get_style_degree(self, confidence: float) -> str:
        """Get style intensity based on confidence level."""
        if confidence > 0.8:
            return "1.5"  # Strong emotion
        elif confidence > 0.6:
            return "1.2"  # Moderate emotion
        else:
            return "1.0"  # Subtle emotion
    
    def _escape_ssml_text(self, text: str) -> str:
        """Escape special characters in SSML."""
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace("\"", "&quot;")
                   .replace("'", "&apos;"))
    
    @staticmethod
    def estimate_duration(text: str) -> float:
        """Estimate audio duration based on text length."""
        # Rough estimation: ~150 words per minute = 2.5 words per second
        word_count = len(text.split())
        return max(1.0, word_count / 2.5)