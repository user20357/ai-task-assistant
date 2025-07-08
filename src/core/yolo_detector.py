"""
YOLO-based Icon Detection System
Detects common UI elements like Chrome icon, close buttons, etc.
"""

import logging
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class YOLOIconDetector:
    """YOLO-based detector for common UI icons and elements"""
    
    def __init__(self):
        self.model = None
        self.icon_templates = {}
        self.confidence_threshold = 0.3
        self._init_detector()
        self._load_icon_templates()
    
    def _init_detector(self):
        """Initialize YOLO model"""
        try:
            # Use YOLOv8 nano model for speed
            self.model = YOLO('yolov8n.pt')
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None
    
    def _load_icon_templates(self):
        """Load icon templates for template matching"""
        # Create templates directory if it doesn't exist
        templates_dir = Path("src/templates")
        templates_dir.mkdir(exist_ok=True)
        
        # Define common UI elements to detect
        self.ui_elements = {
            'chrome_icon': {'color': (66, 133, 244), 'shape': 'circle'},
            'firefox_icon': {'color': (255, 149, 0), 'shape': 'circle'},
            'close_button': {'color': (255, 0, 0), 'shape': 'square'},
            'minimize_button': {'color': (255, 255, 0), 'shape': 'square'},
            'maximize_button': {'color': (0, 255, 0), 'shape': 'square'},
            'start_button': {'color': (0, 120, 215), 'shape': 'rectangle'},
            'search_box': {'color': (255, 255, 255), 'shape': 'rectangle'},
        }
        
        logger.info(f"Loaded {len(self.ui_elements)} UI element templates")
    
    def detect_icons(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect icons and UI elements in screenshot"""
        detections = []
        
        try:
            # YOLO object detection
            yolo_detections = self._yolo_detect(screenshot)
            detections.extend(yolo_detections)
            
            # Template matching for specific icons
            template_detections = self._template_match(screenshot)
            detections.extend(template_detections)
            
            # Color-based detection for common UI elements
            color_detections = self._color_based_detect(screenshot)
            detections.extend(color_detections)
            
            # Remove duplicates and filter by confidence
            detections = self._filter_detections(detections)
            
            logger.info(f"YOLO detector found {len(detections)} icons/elements")
            
        except Exception as e:
            logger.error(f"Icon detection failed: {e}")
        
        return detections
    
    def _yolo_detect(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Use YOLO for general object detection"""
        detections = []
        
        if self.model is None:
            return detections
        
        try:
            # Run YOLO inference
            results = self.model(screenshot, conf=self.confidence_threshold)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Get class name
                        class_name = self.model.names[class_id]
                        
                        # Filter for relevant objects
                        if self._is_relevant_object(class_name):
                            detections.append({
                                'label': f'{class_name}_icon',
                                'box': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(confidence),
                                'action': f'Click on {class_name}',
                                'type': 'yolo_detection'
                            })
        
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
        
        return detections
    
    def _template_match(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Template matching for specific icons"""
        detections = []
        
        # This would use pre-saved icon templates
        # For now, we'll use shape and color detection
        
        return detections
    
    def _color_based_detect(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements based on color and shape"""
        detections = []
        
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
            
            # Detect window control buttons (close, minimize, maximize)
            detections.extend(self._detect_window_controls(screenshot, hsv))
            
            # Detect browser elements
            detections.extend(self._detect_browser_elements(screenshot, hsv))
            
            # Detect common buttons
            detections.extend(self._detect_common_buttons(screenshot, hsv))
            
        except Exception as e:
            logger.error(f"Color-based detection failed: {e}")
        
        return detections
    
    def _detect_window_controls(self, screenshot: np.ndarray, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Detect window control buttons (close, minimize, maximize)"""
        detections = []
        height, width = screenshot.shape[:2]
        
        # Look in the top-right area for window controls
        top_right = screenshot[0:50, width-150:width]
        
        if top_right.size > 0:
            # Detect red close button
            red_mask = cv2.inRange(hsv[0:50, width-150:width], 
                                 np.array([0, 100, 100]), np.array([10, 255, 255]))
            
            contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 50 < area < 500:  # Reasonable size for close button
                    x, y, w, h = cv2.boundingRect(contour)
                    detections.append({
                        'label': 'close_button',
                        'box': [width-150+x, y, width-150+x+w, y+h],
                        'confidence': 0.8,
                        'action': 'Close window',
                        'type': 'window_control'
                    })
        
        return detections
    
    def _detect_browser_elements(self, screenshot: np.ndarray, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Detect browser-specific elements"""
        detections = []
        
        # Detect address bar (usually white/light colored rectangle near top)
        height, width = screenshot.shape[:2]
        top_area = screenshot[0:100, :]
        
        # Look for white/light areas that could be address bars
        gray = cv2.cvtColor(top_area, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Large enough to be address bar
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Address bars are typically wide and short
                if aspect_ratio > 5 and h < 50:
                    detections.append({
                        'label': 'address_bar',
                        'box': [x, y, x+w, y+h],
                        'confidence': 0.6,
                        'action': 'Click to enter URL',
                        'type': 'browser_element'
                    })
        
        return detections
    
    def _detect_common_buttons(self, screenshot: np.ndarray, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Detect common button shapes and colors"""
        detections = []
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 10000:  # Reasonable button size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Buttons are typically rectangular
                if 0.5 < aspect_ratio < 5:
                    detections.append({
                        'label': 'button',
                        'box': [x, y, x+w, y+h],
                        'confidence': 0.5,
                        'action': 'Click button',
                        'type': 'ui_element'
                    })
        
        return detections
    
    def _is_relevant_object(self, class_name: str) -> bool:
        """Check if detected object is relevant for UI guidance"""
        # Focus on objects that might contain UI elements
        relevant_objects = [
            'laptop', 'mouse', 'keyboard', 'cell phone', 'tv', 'monitor',
            'book', 'clock', 'remote', 'scissors'
        ]
        return class_name.lower() in [obj.lower() for obj in relevant_objects]
    
    def _filter_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and deduplicate detections"""
        if not detections:
            return []
        
        # Sort by confidence
        detections.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Remove overlapping detections
        filtered = []
        for detection in detections:
            if not self._overlaps_with_existing(detection, filtered):
                filtered.append(detection)
        
        return filtered[:10]  # Limit to top 10 detections
    
    def _overlaps_with_existing(self, detection: Dict[str, Any], existing: List[Dict[str, Any]]) -> bool:
        """Check if detection overlaps significantly with existing ones"""
        box1 = detection['box']
        
        for existing_detection in existing:
            box2 = existing_detection['box']
            
            # Calculate intersection over union (IoU)
            iou = self._calculate_iou(box1, box2)
            if iou > 0.5:  # 50% overlap threshold
                return True
        
        return False
    
    def _calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """Calculate Intersection over Union of two boxes"""
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
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0