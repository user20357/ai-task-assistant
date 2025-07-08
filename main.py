#!/usr/bin/env python3
"""
Hybrid AI Assistant App - Main Entry Point
A Windows app that guides users through tasks using AI chat and screen overlays.
"""

import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_window import MainWindow
from src.core.app_manager import AppManager

# Parse command line arguments
parser = argparse.ArgumentParser(description='AI Task Assistant')
parser.add_argument('--no-auto-start', action='store_true', help='Disable auto-start of guidance')
args = parser.parse_args()

def main():
    """Main application entry point"""
    try:
        print("Starting AI Task Assistant...")
        
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
        
        # Initialize app manager with command-line arguments
        app_manager = AppManager()
        print("AppManager initialized successfully")
        
        # Set auto-start flag based on command-line argument (disabled by default for debugging)
        app_manager.auto_start_enabled = False  # Temporarily disabled for debugging
        
        # Create and show main window
        main_window = MainWindow(app_manager)
        print("MainWindow created successfully")
        
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        print("MainWindow shown and activated")
        
        # Start the application
        print("Starting event loop...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error in main(): {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()