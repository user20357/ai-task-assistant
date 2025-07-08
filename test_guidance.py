#!/usr/bin/env python3
"""
Test script to verify guidance functionality
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.app_manager import AppManager

def test_guidance():
    """Test the guidance system"""
    print("🧪 Testing AI Task Assistant Guidance System")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create app manager
    app_manager = AppManager()
    
    # Test task readiness
    print("📝 Testing task readiness detection...")
    
    # Simulate a task being ready
    test_task = "Help me upload a file to a website"
    
    def on_task_started(task):
        print(f"✅ Task started: {task}")
        print("🔍 Detection should now be running...")
        
        # Test detection after 3 seconds
        QTimer.singleShot(3000, test_detection)
    
    def test_detection():
        print("🔍 Testing screen detection...")
        try:
            detections = app_manager.screen_detector.detect_screen_elements()
            print(f"✅ Detection completed: {len(detections)} elements found")
            
            if detections:
                for i, detection in enumerate(detections[:3]):
                    print(f"   {i+1}. {detection.get('label', 'Unknown')} - {detection.get('action', 'No action')}")
            
            # Test overlay display
            if detections:
                print("🎯 Testing overlay display...")
                app_manager.overlay_manager.show_overlays(detections, "Test instruction")
                print("✅ Overlays should now be visible on screen")
                
                # Hide overlays after 2 seconds
                QTimer.singleShot(2000, lambda: app_manager.overlay_manager.hide_all_overlays())
            
        except Exception as e:
            print(f"❌ Detection failed: {e}")
        
        # Exit after test
        QTimer.singleShot(5000, app.quit)
    
    # Connect signals
    app_manager.task_started.connect(on_task_started)
    
    # Start guidance
    print("🚀 Starting guidance...")
    app_manager.start_guidance(test_task)
    
    # Run for 10 seconds max
    QTimer.singleShot(10000, app.quit)
    
    print("⏳ Running test... (will exit automatically)")
    return app.exec()

if __name__ == "__main__":
    try:
        test_guidance()
        print("\n✅ Test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)