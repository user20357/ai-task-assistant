#!/usr/bin/env python3
"""
Simple test to check if PyQt6 window shows properly
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    
    # Create a simple window
    window = QMainWindow()
    window.setWindowTitle("Simple Test Window")
    window.setGeometry(100, 100, 400, 300)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Create layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Add a label
    label = QLabel("If you can see this, PyQt6 is working!")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    
    # Show window
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("Window should be visible now")
    
    # Run app
    sys.exit(app.exec())

if __name__ == "__main__":
    main()