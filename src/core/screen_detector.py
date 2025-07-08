"""
Screen Detector - Captures screen and detects UI elements
Uses computer vision and OCR to identify clickable elements.
"""

import os
import io
import base64
import logging
from typing import List, Dict, Any, Optional, Tuple
import requests
import mss
import cv2
import numpy as np
from PIL import Image, ImageDraw
from PyQt6.QtCore import QObject, pyqtSignal
from .yolo_detector import YOLOIconDetector
from .ui_element_detector import UIElementDetector
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class ScreenDetector(QObject):
    """Handles screen capture and element detection"""
    
    # Signals
    detections_ready = pyqtSignal(list)  # List of detected elements
    detection_failed = pyqtSignal(str)   # Error message
    
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        self.detection_confidence = 0.5
        self.max_detections = 10
        
        # Screen capture setup
        self.sct = mss.mss()
        
        # YOLO-based icon detection
        self.yolo_detector = YOLOIconDetector()
        
        # Advanced UI element detection
        self.ui_detector = UIElementDetector()
        
        # Local fallback detection (basic UI elements)
        self.local_detector = LocalUIDetector()
        
        logger.info("ScreenDetector initialized")
    
    def detect_screen_elements(self) -> List[Dict[str, Any]]:
        """Main detection method - captures screen and detects elements"""
        try:
            logger.info("Starting screen element detection...")
            
            # Capture current screen
            screenshot = self._capture_screen()
            if screenshot is None:
                raise Exception("Failed to capture screen")
            
            logger.info(f"Screen captured: {screenshot.shape}")
            
            # Try cloud detection first
            detections = self._detect_with_cloud(screenshot)
            
            # If cloud fails, use advanced UI detection
            if not detections:
                logger.info("Cloud detection failed, trying advanced UI detection")
                detections = self.ui_detector.detect_ui_elements(screenshot)
            
            # If UI detection fails, try YOLO
            if not detections:
                logger.info("UI detection failed, trying YOLO detection")
                yolo_detections = self.yolo_detector.detect_icons(screenshot)
                detections.extend(yolo_detections)
            
            # If all else fails, use basic local detection
            if not detections:
                logger.info("All advanced detection failed, using basic local detection")
                detections = self._detect_locally(screenshot)
            
            # Filter and process detections
            processed_detections = self._process_detections(detections)
            
            # Emit results
            self.detections_ready.emit(processed_detections)
            return processed_detections
            
        except Exception as e:
            logger.error(f"Screen detection failed: {e}")
            self.detection_failed.emit(str(e))
            return []
    
    def _capture_screen(self) -> Optional[np.ndarray]:
        """Capture the current screen"""
        try:
            # Get primary screen
            screen = QApplication.primaryScreen()
            if not screen:
                raise Exception("No primary screen found")
            
            # Get screen geometry
            geometry = screen.geometry()
            
            # Capture using mss (faster than Qt for frequent captures)
            monitor = {
                "top": geometry.y(),
                "left": geometry.x(), 
                "width": geometry.width(),
                "height": geometry.height()
            }
            
            # Take screenshot
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array
            img_array = np.array(screenshot)
            
            # Convert BGRA to RGB
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)
            
            return img_rgb
            
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    def _detect_with_cloud(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Send screenshot to cloud API for detection"""
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(screenshot)
            
            # Resize if too large (to save bandwidth)
            max_size = 1920
            if pil_image.width > max_size or pil_image.height > max_size:
                pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Send to backend
            response = requests.post(
                f"{self.backend_url}/analyze-screenshot",
                json={
                    "image": img_base64,
                    "confidence": self.detection_confidence,
                    "max_detections": self.max_detections
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Cloud detection successful: {len(result.get('detections', []))} detections found")
                return result.get('detections', [])
            else:
                logger.warning(f"Cloud detection failed: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout as e:
            logger.warning(f"Cloud API timeout: {e}")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Cloud API connection error: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.warning(f"Cloud API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Cloud detection error: {e}")
            return []
    
    def _detect_locally(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Fallback local detection using basic computer vision"""
        try:
            return self.local_detector.detect_ui_elements(screenshot)
        except Exception as e:
            logger.error(f"Local detection failed: {e}")
            return []
    
    def _process_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and filter detections"""
        processed = []
        
        for i, detection in enumerate(detections[:self.max_detections]):
            try:
                # Ensure required fields
                if 'box' not in detection or 'label' not in detection:
                    continue
                
                # Add unique ID
                detection['id'] = f"detection_{i}"
                
                # Ensure action field
                if 'action' not in detection:
                    detection['action'] = f"Click {detection['label']}"
                
                # Validate box coordinates
                box = detection['box']
                if len(box) >= 4 and all(isinstance(x, (int, float)) for x in box):
                    processed.append(detection)
                
            except Exception as e:
                logger.warning(f"Failed to process detection {i}: {e}")
                continue
        
        return processed


class LocalUIDetector:
    """Local UI element detection using OpenCV"""
    
    def __init__(self):
        self.button_cascade = None
        self._init_detectors()
    
    def _init_detectors(self):
        """Initialize local detection methods"""
        # For now, we'll use basic shape and color detection
        # Later can be enhanced with trained cascades or templates
        pass
    
    def detect_ui_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements using local computer vision"""
        detections = []
        
        try:
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
            
            # Detect buttons by shape and color
            button_detections = self._detect_buttons(gray, screenshot)
            detections.extend(button_detections)
            
            # Detect text areas using OCR
            text_detections = self._detect_text_areas(gray)
            detections.extend(text_detections)
            
            # Detect common UI patterns
            ui_detections = self._detect_ui_patterns(gray)
            detections.extend(ui_detections)
            
        except Exception as e:
            logger.error(f"Local UI detection failed: {e}")
        
        return detections
    
    def _detect_buttons(self, gray: np.ndarray, color_img: np.ndarray) -> List[Dict[str, Any]]:
        """Detect button-like elements"""
        detections = []
        
        try:
            # Find contours that might be buttons
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by area and aspect ratio
                area = cv2.contourArea(contour)
                if area < 500 or area > 50000:  # Skip too small or too large
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Button-like aspect ratio
                if 0.3 < aspect_ratio < 5.0:
                    detections.append({
                        'label': 'Button',
                        'box': [x, y, x + w, y + h],
                        'action': 'Click this button',
                        'confidence': 0.6
                    })
            
        except Exception as e:
            logger.warning(f"Button detection failed: {e}")
        
        return detections[:5]  # Limit to 5 buttons
    
    def _detect_text_areas(self, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect text input areas"""
        detections = []
        
        try:
            # Simple text area detection using morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 20000:  # Text input size range
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    if aspect_ratio > 2:  # Wide rectangles (typical for text inputs)
                        detections.append({
                            'label': 'Text Input',
                            'box': [x, y, x + w, y + h],
                            'action': 'Click to enter text',
                            'confidence': 0.5
                        })
            
        except Exception as e:
            logger.warning(f"Text area detection failed: {e}")
        
        return detections[:3]  # Limit to 3 text areas
    
    def _detect_ui_patterns(self, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect common UI patterns"""
        detections = []
        
        try:
            # Template matching for common icons (simplified)
            # This would be enhanced with actual icon templates
            
            # For now, detect rectangular regions that might be clickable
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 5000:  # Small clickable elements
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Square-ish elements (might be icons)
                    aspect_ratio = w / h
                    if 0.7 < aspect_ratio < 1.3:
                        detections.append({
                            'label': 'Clickable Element',
                            'box': [x, y, x + w, y + h],
                            'action': 'Click this element',
                            'confidence': 0.4
                        })
            
        except Exception as e:
            logger.warning(f"UI pattern detection failed: {e}")
        
        return detections[:3]  # Limit to 3 patterns