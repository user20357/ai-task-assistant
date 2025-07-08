"""
Advanced UI Element Detection
Focuses on detecting actual clickable UI elements like buttons, text fields, etc.
"""

import logging
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from PIL import Image

# Try to import pytesseract, but make it optional
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available, some text detection features will be limited")

logger = logging.getLogger(__name__)

class UIElementDetector:
    """Advanced detector for UI elements like buttons, text fields, icons"""
    
    def __init__(self):
        self.confidence_threshold = 0.6
        
    def detect_ui_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect actual UI elements that users can interact with"""
        detections = []
        
        try:
            # Convert to different color spaces for better detection
            gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
            
            # Detect different types of UI elements
            detections.extend(self._detect_buttons(screenshot, gray))
            detections.extend(self._detect_text_fields(screenshot, gray))
            detections.extend(self._detect_icons(screenshot, gray))
            detections.extend(self._detect_links(screenshot, gray))
            detections.extend(self._detect_window_controls(screenshot, gray))
            
            # Filter and rank detections
            detections = self._filter_and_rank(detections)
            
            logger.info(f"UI detector found {len(detections)} interactive elements")
            
        except Exception as e:
            logger.error(f"UI element detection failed: {e}")
        
        return detections
    
    def _detect_buttons(self, screenshot: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect button-like elements"""
        detections = []
        
        # Use edge detection to find rectangular shapes
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate to connect nearby edges
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by size (buttons are typically medium-sized)
            if 1000 < area < 50000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Buttons are typically rectangular
                if 0.3 < aspect_ratio < 10:
                    # Check if it looks like a button (has text or is colored)
                    roi = screenshot[y:y+h, x:x+w]
                    if self._looks_like_button(roi):
                        detections.append({
                            'label': 'button',
                            'box': [x, y, x+w, y+h],
                            'confidence': 0.7,
                            'action': 'Click button',
                            'type': 'button'
                        })
        
        return detections
    
    def _detect_text_fields(self, screenshot: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect text input fields"""
        detections = []
        
        # Look for white/light rectangular areas (typical text fields)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours of white areas
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Text fields are typically medium-sized rectangles
            if 2000 < area < 100000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Text fields are typically wide and short
                if aspect_ratio > 2 and h < 100:
                    detections.append({
                        'label': 'text_field',
                        'box': [x, y, x+w, y+h],
                        'confidence': 0.6,
                        'action': 'Click to type text',
                        'type': 'input'
                    })
        
        return detections
    
    def _detect_icons(self, screenshot: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect icon-like elements"""
        detections = []
        
        # Use template matching for common icons
        # For now, detect small square/circular elements that could be icons
        
        # Find small contours that could be icons
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Icons are typically small
            if 100 < area < 5000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Icons are typically square-ish
                if 0.5 < aspect_ratio < 2:
                    detections.append({
                        'label': 'icon',
                        'box': [x, y, x+w, y+h],
                        'confidence': 0.5,
                        'action': 'Click icon',
                        'type': 'icon'
                    })
        
        return detections
    
    def _detect_links(self, screenshot: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect clickable links (often blue text)"""
        detections = []
        
        # Convert to HSV to detect blue colors (common for links)
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
        
        # Define blue color range
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        # Create mask for blue colors
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Find contours in blue areas
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Links are typically small to medium text
            if 50 < area < 10000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Links are typically wider than tall
                if aspect_ratio > 1:
                    detections.append({
                        'label': 'link',
                        'box': [x, y, x+w, y+h],
                        'confidence': 0.6,
                        'action': 'Click link',
                        'type': 'link'
                    })
        
        return detections
    
    def _detect_window_controls(self, screenshot: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Detect window control buttons (close, minimize, maximize)"""
        detections = []
        height, width = screenshot.shape[:2]
        
        # Look in top-right corner for window controls
        if width > 100 and height > 50:
            top_right = screenshot[0:50, width-100:width]
            top_right_gray = gray[0:50, width-100:width]
            
            # Look for small square buttons in top-right
            edges = cv2.Canny(top_right_gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Window controls are small squares
                if 50 < area < 1000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Should be roughly square
                    if 0.5 < aspect_ratio < 2:
                        # Adjust coordinates to full screen
                        full_x = width - 100 + x
                        full_y = y
                        
                        # Determine type based on position (rightmost is usually close)
                        if full_x > width - 50:
                            label = 'close_button'
                            action = 'Close window'
                        elif full_x > width - 80:
                            label = 'maximize_button'
                            action = 'Maximize window'
                        else:
                            label = 'minimize_button'
                            action = 'Minimize window'
                        
                        detections.append({
                            'label': label,
                            'box': [full_x, full_y, full_x+w, full_y+h],
                            'confidence': 0.8,
                            'action': action,
                            'type': 'window_control'
                        })
        
        return detections
    
    def _looks_like_button(self, roi: np.ndarray) -> bool:
        """Check if a region looks like a button"""
        if roi.size == 0:
            return False
        
        # Check if it has text (buttons often have text)
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        
        # Simple check: if there's significant variation in pixel values, it might have text
        std_dev = np.std(gray_roi)
        
        # Also check if it's not just a solid color
        unique_colors = len(np.unique(gray_roi))
        
        return std_dev > 20 and unique_colors > 5
    
    def _filter_and_rank(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter overlapping detections and rank by importance"""
        if not detections:
            return []
        
        # Sort by confidence and type priority
        type_priority = {
            'button': 5,
            'text_field': 4,
            'window_control': 3,
            'link': 2,
            'icon': 1
        }
        
        def get_priority(detection):
            type_score = type_priority.get(detection.get('type', ''), 0)
            confidence = detection.get('confidence', 0)
            return type_score * confidence
        
        detections.sort(key=get_priority, reverse=True)
        
        # Remove overlapping detections
        filtered = []
        for detection in detections:
            if not self._overlaps_significantly(detection, filtered):
                filtered.append(detection)
        
        return filtered[:8]  # Limit to top 8 most important elements
    
    def _overlaps_significantly(self, detection: Dict[str, Any], existing: List[Dict[str, Any]]) -> bool:
        """Check if detection overlaps significantly with existing ones"""
        box1 = detection['box']
        
        for existing_detection in existing:
            box2 = existing_detection['box']
            
            # Calculate overlap
            overlap = self._calculate_overlap(box1, box2)
            if overlap > 0.3:  # 30% overlap threshold
                return True
        
        return False
    
    def _calculate_overlap(self, box1: List[int], box2: List[int]) -> float:
        """Calculate overlap ratio between two boxes"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate areas
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        # Return intersection over smaller area
        smaller_area = min(area1, area2)
        return intersection / smaller_area if smaller_area > 0 else 0.0