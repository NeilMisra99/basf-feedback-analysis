"""Azure Speech service for generating emotion-aware audio responses."""

import os
import logging
from typing import Dict, Any
import azure.cognitiveservices.speech as speechsdk
from .base import BaseExternalService, retry_on_failure, ServiceResponse
from .blob_storage import BlobStorageService

logger = logging.getLogger(__name__)


class AzureSpeechService(BaseExternalService):
    
    def __init__(self):
        super().__init__("Azure Speech")
        self.speech_key = os.environ.get('AZURE_SPEECH_KEY')
        self.speech_region = os.environ.get('AZURE_SPEECH_REGION')
        self.blob_storage = BlobStorageService()
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
            self.speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
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
            
            ssml = self._create_emotion_ssml(text, sentiment, confidence)
            
            if os.environ.get('FLASK_ENV') == 'production':
                audio_dir = os.path.join('/tmp', 'audio_files')
            else:
                audio_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'audio_files')
            
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, f'{feedback_id}.mp3')
            
            audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
                
                logger.info(f"Audio generated successfully: {audio_path} ({file_size} bytes)")
                logger.info(f"Audio directory: {audio_dir}")
                logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
                logger.info(f"File exists check: {os.path.exists(audio_path)}")
                
                blob_url = None
                sas_url = None
                if self.blob_storage.is_available:
                    blob_result = self.blob_storage.upload_audio_file(audio_path, feedback_id)
                    if blob_result.success:
                        blob_url = blob_result.data.get('blob_url')
                        sas_url = blob_result.data.get('sas_url')
                        logger.info(f"Audio uploaded to blob storage: {blob_url}")
                        
                        try:
                            os.remove(audio_path)
                            logger.info(f"Local audio file cleaned up: {audio_path}")
                        except Exception as e:
                            logger.warning(f"Failed to clean up local file: {e}")
                    else:
                        logger.warning(f"Failed to upload to blob storage: {blob_result.error}")
                
                audio_data = {
                    'file_path': audio_path,
                    'file_size': file_size,
                    'voice_used': self._get_voice_for_sentiment(sentiment, confidence),
                    'emotion_style': self._get_emotion_style(sentiment, confidence),
                    'ssml_used': True,
                    'blob_url': blob_url,
                    'sas_url': sas_url
                }
                
                return ServiceResponse(
                    success=True,
                    data=audio_data,
                    service_used="azure_speech"
                )
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speechsdk.CancellationDetails(result)
                logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {cancellation_details.error_details}")
                return ServiceResponse(
                    success=False,
                    error=f"Speech synthesis canceled: {cancellation_details.reason}",
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
        prosody_settings = self._get_prosody_for_sentiment(sentiment, confidence)
        
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice}">
                <mstts:express-as style="{style}" styledegree="{style_degree}">
                    <prosody rate="{prosody_settings['rate']}" pitch="{prosody_settings['pitch']}">
                        {self._escape_ssml_text(text)}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """
        
        return ssml.strip()
    
    def _get_voice_for_sentiment(self, sentiment: str, confidence: float) -> str:
        """Select appropriate voice based on sentiment with proper voice names."""
        voice_mapping = {
            'positive': 'en-US-JennyNeural',    # Supports: cheerful, excited, friendly, hopeful
            'negative': 'en-US-AriaNeural',     # Supports: empathetic, customerservice, hopeful, friendly
            'neutral': 'en-US-AriaNeural'       # Supports: chat, customerservice, friendly
        }
        return voice_mapping.get(sentiment, voice_mapping['neutral'])
    
    def _get_emotion_style(self, sentiment: str, confidence: float) -> str:
        """Get emotion style based on sentiment and confidence using supported styles."""
        if sentiment == 'positive':
            if confidence > 0.95:
                return 'excited'
            elif confidence > 0.9:
                return 'cheerful'
            elif confidence > 0.75:
                return 'hopeful'
            else:
                return 'friendly'
        elif sentiment == 'negative':
            if confidence > 0.95:
                return 'hopeful'
            elif confidence > 0.9:
                return 'empathetic'
            elif confidence > 0.75:
                return 'friendly'
            else:
                return 'customerservice'
        else:
            if confidence > 0.95:
                return 'customerservice'
            elif confidence > 0.9:
                return 'chat'
            elif confidence > 0.75:
                return 'friendly'
            else:
                return 'empathetic'
    
    def _get_style_degree(self, confidence: float) -> str:
        """Get style intensity based on confidence level."""
        if confidence > 0.95:
            return "1.3"
        elif confidence > 0.9:
            return "1.2"
        elif confidence > 0.75:
            return "1.1"
        else:
            return "1.0"
    
    def _get_prosody_for_sentiment(self, sentiment: str, confidence: float) -> dict:
        """Get prosody settings - use engine defaults for rate and pitch."""
        return {'rate': 'default', 'pitch': 'default'}
    
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
        word_count = len(text.split())
        return max(1.0, word_count / 2.5)