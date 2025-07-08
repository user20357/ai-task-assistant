"""
Backend API for AI Task Assistant
Handles screen detection using computer vision and OCR.
"""

import io
import base64
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
from PIL import Image
import easyocr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Task Assistant Backend",
    description="Computer vision API for screen element detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OCR reader
ocr_reader = None

class DetectionRequest(BaseModel):
    image: str  # Base64 encoded image
    confidence: float = 0.5
    max_detections: int = 10

class Detection(BaseModel):
    label: str
    box: List[int]  # [x1, y1, x2, y2]
    action: str
    confidence: float

class DetectionResponse(BaseModel):
    detections: List[Detection]
    processing_time: float

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global ocr_reader
    try:
        logger.info("Initializing OCR reader...")
        ocr_reader = easyocr.Reader(['en'])
        logger.info("Backend initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Task Assistant Backend", "status": "running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ocr_ready": ocr_reader is not None,
        "version": "1.0.0"
    }

@app.post("/detect", response_model=DetectionResponse)
async def detect_elements(request: DetectionRequest):
    """Detect UI elements in screenshot"""
    import time
    start_time = time.time()
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Detect elements
        detections = await _detect_ui_elements(
            img_array, 
            request.confidence, 
            request.max_detections
        )
        
        processing_time = time.time() - start_time
        
        return DetectionResponse(
            detections=detections,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {e}")

async def _detect_ui_elements(image: np.ndarray, confidence: float, max_detections: int) -> List[Detection]:
    """Detect UI elements using computer vision"""
    detections = []
    
    try:
        # Convert to different formats for processing
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 1. Detect buttons using contour detection
        button_detections = _detect_buttons(gray, image)
        detections.extend(button_detections)
        
        # 2. Detect text using OCR
        if ocr_reader:
            text_detections = _detect_text_with_ocr(image)
            detections.extend(text_detections)
        
        # 3. Detect common UI patterns
        ui_detections = _detect_ui_patterns(gray)
        detections.extend(ui_detections)
        
        # Filter by confidence and limit results
        filtered_detections = [
            d for d in detections 
            if d.confidence >= confidence
        ][:max_detections]
        
        logger.info(f"Detected {len(filtered_detections)} elements")
        return filtered_detections
        
    except Exception as e:
        logger.error(f"Element detection failed: {e}")
        return []

def _detect_buttons(gray: np.ndarray, color_img: np.ndarray) -> List[Detection]:
    """Detect button-like elements"""
    detections = []
    
    try:
        # Find contours that might be buttons
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Filter by area and aspect ratio
            area = cv2.contourArea(contour)
            if area < 500 or area > 50000:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Button-like aspect ratio
            if 0.3 < aspect_ratio < 5.0:
                detections.append(Detection(
                    label="Button",
                    box=[x, y, x + w, y + h],
                    action="Click this button",
                    confidence=0.6
                ))
        
    except Exception as e:
        logger.warning(f"Button detection failed: {e}")
    
    return detections[:5]  # Limit to 5 buttons

def _detect_text_with_ocr(image: np.ndarray) -> List[Detection]:
    """Detect text areas using OCR"""
    detections = []
    
    try:
        if not ocr_reader:
            return detections
        
        # Run OCR
        results = ocr_reader.readtext(image)
        
        for (bbox, text, confidence) in results:
            if confidence > 0.5 and len(text.strip()) > 2:
                # Convert bbox to rectangle coordinates
                bbox = np.array(bbox).astype(int)
                x1, y1 = bbox.min(axis=0)
                x2, y2 = bbox.max(axis=0)
                
                # Determine if it's clickable text
                action = "Click this text" if _is_clickable_text(text) else "Text area"
                
                detections.append(Detection(
                    label=f"Text: {text[:20]}",
                    box=[x1, y1, x2, y2],
                    action=action,
                    confidence=confidence
                ))
        
    except Exception as e:
        logger.warning(f"OCR detection failed: {e}")
    
    return detections[:8]  # Limit to 8 text elements

def _is_clickable_text(text: str) -> bool:
    """Determine if text is likely clickable"""
    clickable_keywords = [
        'submit', 'send', 'login', 'sign in', 'register', 'download',
        'upload', 'save', 'cancel', 'ok', 'yes', 'no', 'continue',
        'next', 'back', 'home', 'menu', 'settings', 'help'
    ]
    
    text_lower = text.lower().strip()
    return any(keyword in text_lower for keyword in clickable_keywords)

def _detect_ui_patterns(gray: np.ndarray) -> List[Detection]:
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
                    detections.append(Detection(
                        label="UI Element",
                        box=[x, y, x + w, y + h],
                        action="Click this element",
                        confidence=0.4
                    ))
        
    except Exception as e:
        logger.warning(f"UI pattern detection failed: {e}")
    
    return detections[:3]  # Limit to 3 patterns

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (for cloud deployment) or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)