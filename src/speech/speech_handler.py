"""
Speech handling for voice input and output
"""

import logging
import io
import tempfile
from typing import Optional
from fastapi import UploadFile
from google.cloud import speech_v1, texttospeech
from google.cloud.speech_v1 import RecognitionAudio, RecognitionConfig
from google.cloud.texttospeech import SynthesisInput, VoiceSelectionParams, AudioConfig

from src.utils.config import Config

logger = logging.getLogger(__name__)

class SpeechHandler:
    """Handles speech-to-text and text-to-speech operations"""
    
    def __init__(self):
        self.config = Config()
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup Google Cloud Speech clients"""
        try:
            # Speech-to-Text client
            self.speech_client = speech_v1.SpeechClient()
            
            # Text-to-Speech client
            self.tts_client = texttospeech.TextToSpeechClient()
            
            logger.info("Speech clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up speech clients: {e}")
            self.speech_client = None
            self.tts_client = None
    
    async def speech_to_text(self, audio_file: UploadFile) -> str:
        """Convert speech audio to text"""
        try:
            if not self.speech_client:
                raise Exception("Speech client not initialized")
            
            # Read audio file
            audio_content = await audio_file.read()
            
            # Configure recognition
            config = RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.config.speech_sample_rate,
                language_code=self.config.speech_language_code,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
                enable_word_confidence=True,
            )
            
            # Create recognition audio
            audio = RecognitionAudio(content=audio_content)
            
            # Perform recognition
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Extract transcript
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            transcript = transcript.strip()
            logger.info(f"Speech-to-text result: {transcript}")
            
            return transcript
            
        except Exception as e:
            logger.error(f"Error in speech-to-text conversion: {e}")
            raise
    
    async def text_to_speech(self, text: str, output_format: str = "mp3") -> bytes:
        """Convert text to speech audio"""
        try:
            if not self.tts_client:
                raise Exception("Text-to-speech client not initialized")
            
            # Set up synthesis input
            synthesis_input = SynthesisInput(text=text)
            
            # Configure voice
            voice = VoiceSelectionParams(
                language_code=self.config.speech_language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Configure audio
            audio_config = AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            logger.info(f"Text-to-speech conversion completed for: {text[:50]}...")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            raise
    
    async def process_audio_file(self, audio_file: UploadFile) -> str:
        """Process audio file and return transcript"""
        try:
            # Validate file type
            if not audio_file.content_type.startswith('audio/'):
                raise ValueError("File must be an audio file")
            
            # Convert to text
            transcript = await self.speech_to_text(audio_file)
            
            if not transcript:
                raise ValueError("No speech detected in audio file")
            
            return transcript
            
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if speech services are available"""
        return self.speech_client is not None and self.tts_client is not None 