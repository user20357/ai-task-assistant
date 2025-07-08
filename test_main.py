#!/usr/bin/env python3
"""
Test script to debug main.py issues
"""

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Test main application entry point"""
    try:
        print("Starting application...")
        
        # Enable high DPI scaling (PyQt6 compatible)
        try:
            QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        except AttributeError:
            pass  # Not available in all PyQt6 versions
        
        app = QApplication(sys.argv)
        app.setApplicationName("AI Task Assistant")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AI Assistant")
        
        print("QApplication created successfully")
        
        # Import and initialize app manager
        from src.core.app_manager import AppManager
        print("AppManager imported successfully")
        
        app_manager = AppManager()
        print("AppManager initialized successfully")
        
        # Import and create main window
        from src.ui.main_window import MainWindow
        print("MainWindow imported successfully")
        
        main_window = MainWindow(app_manager)
        print("MainWindow created successfully")
        
        main_window.show()
        print("MainWindow shown successfully")
        
        # Start the application
        print("Starting event loop...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()