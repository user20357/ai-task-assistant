"""
Text-to-Speech Manager - Handles voice output for the AI assistant
Provides audio feedback and instructions to users.
"""

import os
import logging
from typing import Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import pyttsx3

logger = logging.getLogger(__name__)

class TTSManager(QObject):
    """Manages text-to-speech functionality"""
    
    # Signals
    speech_started = pyqtSignal(str)  # text being spoken
    speech_finished = pyqtSignal()
    speech_error = pyqtSignal(str)    # error message
    
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.enabled = os.getenv('TTS_ENABLED', 'true').lower() == 'true'
        self.rate = int(os.getenv('TTS_RATE', '200'))
        self.voice = os.getenv('TTS_VOICE', 'default')
        
        # TTS engine
        self.engine = None
        self.is_speaking = False
        
        # Initialize if enabled
        if self.enabled:
            self._init_engine()
        
        logger.info(f"TTSManager initialized (enabled: {self.enabled})")
    
    def _init_engine(self):
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            self.engine.setProperty('rate', self.rate)
            
            # Set voice if specified
            if self.voice != 'default':
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if self.voice.lower() in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set up callbacks
            self.engine.connect('started-utterance', self._on_speech_started)
            self.engine.connect('finished-utterance', self._on_speech_finished)
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.enabled = False
            self.speech_error.emit(f"TTS initialization failed: {e}")
    
    def speak(self, text: str, interrupt: bool = False) -> bool:
        """Speak the given text"""
        if not self.enabled or not self.engine:
            return False
        
        try:
            # Stop current speech if interrupting
            if interrupt and self.is_speaking:
                self.stop()
            
            # Skip if already speaking and not interrupting
            if self.is_speaking and not interrupt:
                logger.info("TTS busy, skipping speech")
                return False
            
            # Clean text for speech
            clean_text = self._clean_text_for_speech(text)
            
            if not clean_text.strip():
                return False
            
            # Start speaking in a separate thread
            speech_thread = SpeechThread(self.engine, clean_text)
            speech_thread.speech_started.connect(self._handle_speech_started)
            speech_thread.speech_finished.connect(self._handle_speech_finished)
            speech_thread.speech_error.connect(self._handle_speech_error)
            speech_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to speak text: {e}")
            self.speech_error.emit(f"Speech failed: {e}")
            return False
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove markdown formatting
        clean_text = text.replace('**', '').replace('*', '')
        clean_text = clean_text.replace('_', ' ')
        
        # Remove special characters that might cause issues
        clean_text = clean_text.replace('•', 'bullet point:')
        clean_text = clean_text.replace('→', 'then')
        clean_text = clean_text.replace('🎯', '')
        clean_text = clean_text.replace('❌', 'X')
        
        # Replace common abbreviations
        replacements = {
            'UI': 'user interface',
            'API': 'A P I',
            'URL': 'U R L',
            'PDF': 'P D F',
            'HTML': 'H T M L',
            'CSS': 'C S S',
            'JS': 'JavaScript'
        }
        
        for abbr, replacement in replacements.items():
            clean_text = clean_text.replace(abbr, replacement)
        
        return clean_text
    
    def stop(self):
        """Stop current speech"""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                logger.info("Speech stopped")
            except Exception as e:
                logger.error(f"Failed to stop speech: {e}")
    
    def set_rate(self, rate: int):
        """Set speech rate"""
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
                self.rate = rate
                logger.info(f"Speech rate set to {rate}")
            except Exception as e:
                logger.error(f"Failed to set speech rate: {e}")
    
    def set_voice(self, voice_name: str):
        """Set voice by name"""
        if self.engine:
            try:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice_name.lower() in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        self.voice = voice_name
                        logger.info(f"Voice set to {voice.name}")
                        return True
                
                logger.warning(f"Voice '{voice_name}' not found")
                return False
                
            except Exception as e:
                logger.error(f"Failed to set voice: {e}")
                return False
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            return [{'id': voice.id, 'name': voice.name} for voice in voices]
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            return []
    
    def _on_speech_started(self, name):
        """Callback when speech starts"""
        self.is_speaking = True
    
    def _on_speech_finished(self, name, completed):
        """Callback when speech finishes"""
        self.is_speaking = False
    
    def _handle_speech_started(self, text: str):
        """Handle speech started signal"""
        self.is_speaking = True
        self.speech_started.emit(text)
    
    def _handle_speech_finished(self):
        """Handle speech finished signal"""
        self.is_speaking = False
        self.speech_finished.emit()
    
    def _handle_speech_error(self, error: str):
        """Handle speech error signal"""
        self.is_speaking = False
        self.speech_error.emit(error)
    
    def is_enabled(self) -> bool:
        """Check if TTS is enabled"""
        return self.enabled
    
    def enable(self):
        """Enable TTS"""
        if not self.enabled:
            self.enabled = True
            if not self.engine:
                self._init_engine()
    
    def disable(self):
        """Disable TTS"""
        if self.enabled:
            self.stop()
            self.enabled = False


class SpeechThread(QThread):
    """Thread for handling TTS to avoid blocking UI"""
    
    speech_started = pyqtSignal(str)
    speech_finished = pyqtSignal()
    speech_error = pyqtSignal(str)
    
    def __init__(self, engine, text: str):
        super().__init__()
        self.engine = engine
        self.text = text
    
    def run(self):
        """Run speech in thread"""
        try:
            self.speech_started.emit(self.text)
            self.engine.say(self.text)
            self.engine.runAndWait()
            self.speech_finished.emit()
            
        except Exception as e:
            logger.error(f"Speech thread error: {e}")
            self.speech_error.emit(str(e))