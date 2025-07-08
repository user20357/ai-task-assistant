#!/usr/bin/env python3
"""
Test script for YOLO-based visual guidance
"""

import sys
import os
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.yolo_detector import YOLOIconDetector
from core.screen_detector import ScreenDetector
import numpy as np

def test_yolo_detection():
    """Test YOLO icon detection"""
    print("🧪 Testing YOLO Icon Detection")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # Create YOLO detector
    yolo_detector = YOLOIconDetector()
    
    # Create screen detector
    screen_detector = ScreenDetector()
    
    def run_test():
        print("📸 Capturing screen...")
        
        try:
            # Test screen detection
            detections = screen_detector.detect_screen_elements()
            
            print(f"✅ Found {len(detections)} elements:")
            for i, detection in enumerate(detections[:5]):  # Show first 5
                print(f"   {i+1}. {detection.get('label', 'Unknown')}")
                print(f"      Box: {detection.get('box', [])}")
                print(f"      Action: {detection.get('action', 'No action')}")
                print(f"      Confidence: {detection.get('confidence', 0):.2f}")
                print()
            
            if detections:
                print("🎯 RED squares should appear on screen!")
            else:
                print("❌ No elements detected")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Exit after test
        QTimer.singleShot(3000, app.quit)
    
    # Run test after app starts
    QTimer.singleShot(1000, run_test)
    
    print("⏳ Starting test... (will show results in 1 second)")
    return app.exec()

if __name__ == "__main__":
    try:
        test_yolo_detection()
        print("\n✅ Test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)