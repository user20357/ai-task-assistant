#!/usr/bin/env python3
"""
Debug script to test the app step by step
"""

import sys
import os
import logging

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.ai_chat import AIChatManager

def test_task_detection():
    """Test if task readiness detection works"""
    print("🧪 Testing Task Readiness Detection")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # Create AI chat manager
    chat_manager = AIChatManager()
    
    # Track task ready signals
    task_ready_received = False
    
    def on_task_ready(task):
        nonlocal task_ready_received
        task_ready_received = True
        print(f"✅ TASK READY SIGNAL RECEIVED: {task}")
        app.quit()
    
    # Connect signal
    chat_manager.task_ready.connect(on_task_ready)
    
    # Test conversation
    print("📝 Starting test conversation...")
    
    def send_test_messages():
        print("👤 User: Help me upload a file")
        response1 = chat_manager.send_message("Help me upload a file")
        print(f"🤖 AI: {response1}")
        
        # Wait and send follow-up
        QTimer.singleShot(1000, send_followup)
    
    def send_followup():
        print("👤 User: I have a PDF file ready")
        response2 = chat_manager.send_message("I have a PDF file ready")
        print(f"🤖 AI: {response2}")
        
        # Check if task ready was triggered
        QTimer.singleShot(2000, check_result)
    
    def check_result():
        if task_ready_received:
            print("✅ Task readiness detection WORKING!")
        else:
            print("❌ Task readiness detection NOT WORKING")
            print("🔍 Checking conversation history...")
            for i, msg in enumerate(chat_manager.conversation_history):
                print(f"   {i}: {msg['role']}: {msg['content'][:100]}...")
        
        app.quit()
    
    # Start test
    QTimer.singleShot(500, send_test_messages)
    
    # Timeout after 10 seconds
    QTimer.singleShot(10000, app.quit)
    
    return app.exec()

if __name__ == "__main__":
    try:
        test_task_detection()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()