"""
App Manager - Central coordinator for the AI Assistant
Manages the flow between chat, screen detection, and overlay systems.
"""

import os
import logging
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from .ai_chat import AIChatManager
from .screen_detector import ScreenDetector
from .overlay_manager import OverlayManager
from .tts_manager import TTSManager
from .performance_optimizer import PerformanceOptimizer
from ..utils.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppManager(QObject):
    """Central manager coordinating all app components"""
    
    # Signals
    task_ready = pyqtSignal(str)    # Task description when ready but not started
    task_started = pyqtSignal(str)  # Task description when guidance starts
    task_completed = pyqtSignal()
    guidance_paused = pyqtSignal()
    guidance_resumed = pyqtSignal()
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self):
        super().__init__()
        
        # App state
        self.current_task = ""
        self.is_guidance_active = False
        self.is_paused = False
        self.auto_start_enabled = False  # Default to false, can be enabled via command-line
        
        # Initialize components
        self._init_components()
        
        # Setup connections
        self._setup_connections()
        
        logger.info("AppManager initialized successfully")
    
    def _init_components(self):
        """Initialize all app components"""
        try:
            # AI Chat Manager
            self.chat_manager = AIChatManager()
            
            # Screen Detection System
            self.screen_detector = ScreenDetector()
            
            # Overlay Manager
            self.overlay_manager = OverlayManager()
            
            # Text-to-Speech Manager
            self.tts_manager = TTSManager()
            
            # Performance Optimizer
            self.performance_optimizer = PerformanceOptimizer()
            
            # Memory Manager
            self.memory_manager = MemoryManager()
            
            # Detection timer
            self.detection_timer = QTimer()
            self.detection_timer.timeout.connect(self._perform_detection)
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            self.error_occurred.emit(f"Initialization error: {e}")
    
    def _setup_connections(self):
        """Setup signal connections between components"""
        # Chat manager connections
        self.chat_manager.task_ready.connect(self._on_task_ready)
        self.chat_manager.user_needs_help.connect(self._handle_user_help)
        
        # Screen detector connections
        self.screen_detector.detections_ready.connect(self._handle_detections)
        self.screen_detector.detection_failed.connect(self._handle_detection_failure)
        
        # Overlay manager connections
        self.overlay_manager.user_clicked_element.connect(self._handle_user_click)
    
    def start_chat_session(self) -> bool:
        """Start initial chat session with user"""
        try:
            return self.chat_manager.start_session()
        except Exception as e:
            logger.error(f"Failed to start chat session: {e}")
            self.error_occurred.emit(f"Chat error: {e}")
            return False
    
    def start_guidance(self, task_description: str):
        """Start the guidance mode"""
        try:
            self.current_task = task_description
            self.is_guidance_active = True
            self.is_paused = False
            
            logger.info(f"Starting guidance for task: {task_description}")
            
            # Start performance optimization
            self.performance_optimizer.start_optimization()
            
            # Start memory monitoring
            self.memory_manager.start_monitoring()
            
            # Start screen detection with optimal interval
            self.detection_timer.start(self.performance_optimizer.get_optimal_detection_interval())
            
            # Switch to guidance mode and show first step
            try:
                self.chat_manager.switch_to_guidance_mode()
            except Exception as e:
                logger.error(f"Failed to switch to guidance mode: {e}")
            
            # Show floating chat
            try:
                self.chat_manager.switch_to_floating_mode()
            except Exception as e:
                logger.error(f"Failed to switch to floating mode: {e}")
            
            # Emit signal
            self.task_started.emit(task_description)
            
        except Exception as e:
            logger.error(f"Failed to start guidance: {e}")
            self.error_occurred.emit(f"Guidance error: {e}")
    
    def pause_guidance(self):
        """Pause the guidance system"""
        if self.is_guidance_active and not self.is_paused:
            self.is_paused = True
            self.detection_timer.stop()
            self.overlay_manager.hide_all_overlays()
            self.guidance_paused.emit()
            logger.info("Guidance paused")
    
    def resume_guidance(self):
        """Resume the guidance system"""
        if self.is_guidance_active and self.is_paused:
            self.is_paused = False
            self.detection_timer.start(self.performance_optimizer.get_optimal_detection_interval())
            self.guidance_resumed.emit()
            logger.info("Guidance resumed")
    
    def stop_guidance(self):
        """Stop the guidance system"""
        try:
            self.is_guidance_active = False
            self.is_paused = False
            
            # Stop detection timer
            self.detection_timer.stop()
            
            # Stop performance optimization
            self.performance_optimizer.stop_optimization()
            
            # Stop memory monitoring
            self.memory_manager.stop_monitoring()
            
            # Hide overlays
            self.overlay_manager.hide_all_overlays()
            
            # Switch chat back to normal mode
            self.chat_manager.switch_to_normal_mode()
            
            self.task_completed.emit()
            logger.info("Guidance stopped")
        except Exception as e:
            logger.error(f"Failed to stop guidance: {e}")
    
    def _perform_detection(self):
        """Perform screen detection cycle"""
        if not self.is_guidance_active or self.is_paused:
            return
        
        # Set a timeout to prevent hanging
        recovery_timer = QTimer()
        recovery_timer.setSingleShot(True)
        recovery_timer.timeout.connect(self._detection_timeout_recovery)
        recovery_timer.start(10000)  # 10 second timeout
        
        try:
            # Update detection interval based on current system load
            interval = self.performance_optimizer.get_optimal_detection_interval()
            self.detection_timer.setInterval(interval)
            
            # Capture screen and detect elements
            detections = self.screen_detector.detect_screen_elements()
            logger.info(f"Detection cycle completed, found {len(detections) if detections else 0} elements")
            
            # Cancel recovery timer since we completed successfully
            recovery_timer.stop()
            
        except Exception as e:
            logger.error(f"Detection cycle failed: {e}")
            self._handle_detection_failure(str(e))
            recovery_timer.stop()
    
    def _detection_timeout_recovery(self):
        """Recovery method if detection hangs"""
        logger.warning("Detection timeout occurred - attempting recovery")
        
        try:
            # Hide any existing overlays
            self.overlay_manager.hide_all_overlays()
            
            # Show recovery message
            self.overlay_manager._show_instruction_panel("Detection timed out. Click anywhere to continue.")
            
            # Restart detection after a delay
            QTimer.singleShot(5000, self._perform_detection)
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            # Last resort - try to restart guidance
            self.stop_guidance()
            QTimer.singleShot(1000, lambda: self.start_guidance("Restarted after recovery"))
    
    def _handle_detections(self, detections: list):
        """Handle detected screen elements"""
        try:
            if not detections:
                # No detections found
                self.overlay_manager.hide_all_overlays()
                logger.info("No UI elements detected - hiding overlays")
                return
                
            # Limit number of detections to prevent performance issues
            max_elements = 5
            if len(detections) > max_elements:
                logger.info(f"Limiting detections from {len(detections)} to {max_elements} to improve performance")
                detections = detections[:max_elements]
            
            # Create detection summary for AI
            detection_summary = self._create_detection_summary(detections)
            
            # Get current step guidance from AI with red square context
            try:
                current_step = self.chat_manager.get_current_step_guidance_with_detections(detection_summary)
                instruction = current_step if current_step else "Click on a RED square to continue"
            except Exception as chat_error:
                logger.error(f"Failed to get guidance from AI: {chat_error}")
                instruction = "Click on a RED square to continue (AI guidance unavailable)"
            
            # Show RED overlays for relevant elements with clear instructions
            self.overlay_manager.show_overlays(detections, instruction)
            
            logger.info(f"Showing {len(detections)} RED squares on screen")
            
        except Exception as e:
            logger.error(f"Failed to handle detections: {e}")
            # Try to recover by hiding overlays
            try:
                self.overlay_manager.hide_all_overlays()
            except:
                pass
    
    def _create_detection_summary(self, detections: list) -> str:
        """Create a summary of detected elements for AI"""
        if not detections:
            return "No clickable elements detected on screen."
        
        summary = f"I can see {len(detections)} RED squares on the screen highlighting these elements:\n"
        
        for i, detection in enumerate(detections[:5], 1):  # Limit to first 5
            label = detection.get('label', 'unknown')
            action = detection.get('action', 'click')
            summary += f"{i}. RED SQUARE around {label} - {action}\n"
        
        if len(detections) > 5:
            summary += f"...and {len(detections) - 5} more elements\n"
        
        summary += "\nWhich RED SQUARE should I click for the next step?"
        return summary
    
    def _handle_detection_failure(self, error_msg: str):
        """Handle detection failures"""
        logger.warning(f"Detection failed: {error_msg}")
        
        # Pause briefly and retry
        QTimer.singleShot(5000, self._perform_detection)
    
    def _handle_user_click(self, element_info: Dict[str, Any]):
        """Handle user clicking on an overlay element"""
        try:
            # Notify chat manager about user action
            self.chat_manager.handle_user_action(element_info)
            
            # Hide the clicked overlay
            self.overlay_manager.hide_overlay(element_info.get('id'))
            
        except Exception as e:
            logger.error(f"Failed to handle user click: {e}")
    
    def _handle_user_help(self, help_request: str):
        """Handle user asking for help"""
        try:
            # Pause detection temporarily
            was_active = not self.is_paused
            if was_active:
                self.pause_guidance()
            
            # Get help response from AI
            help_response = self.chat_manager.get_help_response(help_request)
            
            # Speak the response if TTS is enabled
            if help_response:
                self.tts_manager.speak(help_response)
            
            # Resume if it was active
            if was_active:
                QTimer.singleShot(3000, self.resume_guidance)
                
        except Exception as e:
            logger.error(f"Failed to handle help request: {e}")
    
    def _on_task_ready(self, task_description: str):
        """Handle task ready signal from chat manager"""
        # Store the task description
        self.current_task = task_description
        
        # Forward the signal to the UI
        self.task_ready.emit(task_description)
        
        logger.info(f"Task ready: {task_description}")
        
        # Only auto-start if enabled (via command-line argument)
        if self.auto_start_enabled:
            logger.info("Auto-start enabled, starting guidance automatically")
            QTimer.singleShot(1000, lambda: self.start_guidance(task_description))
        else:
            logger.info("Auto-start disabled, waiting for user to click Start Guidance button")
    
    def get_app_status(self) -> Dict[str, Any]:
        """Get current app status"""
        return {
            'current_task': self.current_task,
            'is_guidance_active': self.is_guidance_active,
            'is_paused': self.is_paused,
            'chat_active': self.chat_manager.is_active() if hasattr(self.chat_manager, 'is_active') else False
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop all timers
            self.detection_timer.stop()
            
            # Stop performance optimization
            try:
                self.performance_optimizer.stop_optimization()
            except Exception as e:
                logger.error(f"Failed to stop performance optimizer: {e}")
                
            # Stop memory monitoring
            try:
                self.memory_manager.stop_monitoring()
            except Exception as e:
                logger.error(f"Failed to stop memory manager: {e}")
            
            # Hide all overlays
            try:
                self.overlay_manager.hide_all_overlays()
            except Exception as e:
                logger.error(f"Failed to hide overlays: {e}")
            
            # Stop TTS
            try:
                self.tts_manager.stop()
            except Exception as e:
                logger.error(f"Failed to stop TTS: {e}")
            
            # Force garbage collection to free memory
            import gc
            gc.collect()
            
            logger.info("AppManager cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            # Last resort - try to force exit
            import sys
            sys.exit(1)