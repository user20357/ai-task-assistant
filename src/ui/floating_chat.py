"""
Floating Chat Widget - Minimized chat interface during guidance mode
Provides quick access to AI help while user performs tasks.
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QLabel, QFrame, QApplication)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QBrush, QColor

logger = logging.getLogger(__name__)

class FloatingChatWidget(QWidget):
    """Floating chat widget for guidance mode"""
    
    def __init__(self, app_manager):
        super().__init__()
        
        self.app_manager = app_manager
        self.is_expanded = True  # Start expanded
        self.is_dragging = False
        self.drag_position = None
        
        self._setup_ui()
        self._setup_connections()
        self._setup_animations()
        
        logger.info("FloatingChatWidget initialized")
    
    def _setup_ui(self):
        """Setup floating chat UI"""
        # Window flags for floating behavior - make sure it's interactive
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Make window translucent but keep it interactive
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Ensure the widget accepts focus and mouse events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        
        # Set initial size and position
        self.setFixedSize(350, 360)  # Expanded size
        self._position_window()
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create collapsed and expanded views
        self._create_collapsed_view()
        self._create_expanded_view()
        
        # Start in expanded mode
        self.collapsed_widget.hide()
        
        # Make sure it's visible and active
        self.raise_()
    
    def _create_collapsed_view(self):
        """Create collapsed view"""
        self.collapsed_widget = QFrame()
        self.collapsed_widget.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 20px;
                border: 2px solid #4CAF50;
            }
        """)
        
        layout = QHBoxLayout(self.collapsed_widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # AI icon and status
        status_label = QLabel("🤖 AI Assistant")
        status_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        # Expand button
        expand_btn = QPushButton("💬")
        expand_btn.setFixedSize(30, 30)
        expand_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        expand_btn.clicked.connect(self._toggle_expanded)
        layout.addWidget(expand_btn)
        
        self.main_layout.addWidget(self.collapsed_widget)
    
    def _create_expanded_view(self):
        """Create expanded view"""
        self.expanded_widget = QFrame()
        
        # Make it more visible and attention-grabbing
        self.expanded_widget.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 250);
                border-radius: 15px;
                border: 3px solid #FF5722;
            }
        """)
        
        layout = QVBoxLayout(self.expanded_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🤖 AI Assistant")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Control buttons
        pause_btn = QPushButton("⏸️")
        pause_btn.setFixedSize(25, 25)
        pause_btn.setToolTip("Pause guidance")
        pause_btn.clicked.connect(self._pause_guidance)
        pause_btn.setStyleSheet(self._get_control_button_style())
        header_layout.addWidget(pause_btn)
        
        stop_btn = QPushButton("⏹️")
        stop_btn.setFixedSize(25, 25)
        stop_btn.setToolTip("Stop guidance")
        stop_btn.clicked.connect(self._stop_guidance)
        stop_btn.setStyleSheet(self._get_control_button_style())
        header_layout.addWidget(stop_btn)
        
        collapse_btn = QPushButton("➖")
        collapse_btn.setFixedSize(25, 25)
        collapse_btn.setToolTip("Minimize")
        collapse_btn.clicked.connect(self._toggle_expanded)
        collapse_btn.setStyleSheet(self._get_control_button_style())
        header_layout.addWidget(collapse_btn)
        
        layout.addLayout(header_layout)
        
        # Chat area
        self.mini_chat = QTextEdit()
        self.mini_chat.setMaximumHeight(150)
        self.mini_chat.setReadOnly(True)
        self.mini_chat.setStyleSheet("""
            QTextEdit {
                background-color: rgba(50, 50, 50, 180);
                color: white;
                border: 1px solid #666;
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.mini_chat)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.mini_input = QLineEdit()
        self.mini_input.setPlaceholderText("Ask for help...")
        self.mini_input.returnPressed.connect(self._send_help_message)
        
        # Make input field more visible and responsive
        self.mini_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(60, 60, 60, 250);
                color: white;
                border: 2px solid #FF9800;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #FFEB3B;
                background-color: rgba(70, 70, 70, 255);
            }
        """)
        
        # Ensure it can receive focus
        self.mini_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        input_layout.addWidget(self.mini_input)
        
        send_btn = QPushButton("SEND")
        send_btn.clicked.connect(self._send_help_message)
        
        # Make button more visible and attention-grabbing
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF7043;
            }
            QPushButton:pressed {
                background-color: #E64A19;
            }
        """)
        
        # Make button larger
        send_btn.setMinimumHeight(35)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        # Quick help buttons
        quick_layout = QHBoxLayout()
        
        stuck_btn = QPushButton("I'm stuck")
        stuck_btn.clicked.connect(lambda: self._send_quick_help("I'm stuck"))
        stuck_btn.setStyleSheet(self._get_quick_button_style())
        quick_layout.addWidget(stuck_btn)
        
        next_btn = QPushButton("What's next?")
        next_btn.clicked.connect(lambda: self._send_quick_help("What should I do next?"))
        next_btn.setStyleSheet(self._get_quick_button_style())
        quick_layout.addWidget(next_btn)
        
        layout.addLayout(quick_layout)
        
        self.main_layout.addWidget(self.expanded_widget)
    
    def _get_control_button_style(self) -> str:
        """Get style for control buttons"""
        return """
            QPushButton {
                background-color: rgba(100, 100, 100, 150);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(120, 120, 120, 200);
            }
        """
    
    def _get_quick_button_style(self) -> str:
        """Get style for quick help buttons"""
        return """
            QPushButton {
                background-color: rgba(33, 150, 243, 220);
                color: white;
                border: 2px solid #2196F3;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 255);
                border: 2px solid #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Connect to chat manager for messages
        self.app_manager.chat_manager.message_received.connect(self._on_message_received)
        
        # Connect to app manager for status updates
        self.app_manager.guidance_paused.connect(self._on_guidance_paused)
        self.app_manager.guidance_resumed.connect(self._on_guidance_resumed)
        
        # Set up a timer to ensure the chat remains interactive
        self.visibility_timer = QTimer(self)
        self.visibility_timer.timeout.connect(self._ensure_visibility)
        self.visibility_timer.start(5000)  # Check every 5 seconds
    
    def _setup_animations(self):
        """Setup animations for expand/collapse"""
        self.resize_animation = QPropertyAnimation(self, b"geometry")
        self.resize_animation.setDuration(300)
        self.resize_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _position_window(self):
        """Position window on screen"""
        # Position at bottom-right corner
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 100  # Above taskbar
        
        self.move(x, y)
    
    def _toggle_expanded(self):
        """Toggle between expanded and collapsed states"""
        if self.is_expanded:
            self._collapse()
        else:
            self._expand()
    
    def _expand(self):
        """Expand to full chat interface"""
        self.is_expanded = True
        
        # Show expanded widget
        self.expanded_widget.show()
        self.collapsed_widget.hide()
        
        # Animate resize
        current_rect = self.geometry()
        new_rect = QRect(
            current_rect.x(),
            current_rect.y() - 300,  # Move up
            350,  # Wider
            360   # Taller
        )
        
        self.resize_animation.setStartValue(current_rect)
        self.resize_animation.setEndValue(new_rect)
        self.resize_animation.start()
        
        # Focus input
        QTimer.singleShot(350, lambda: self.mini_input.setFocus())
    
    def _collapse(self):
        """Collapse to minimal interface"""
        self.is_expanded = False
        
        # Show collapsed widget
        self.collapsed_widget.show()
        self.expanded_widget.hide()
        
        # Animate resize
        current_rect = self.geometry()
        new_rect = QRect(
            current_rect.x(),
            current_rect.y() + 300,  # Move down
            300,  # Narrower
            60    # Shorter
        )
        
        self.resize_animation.setStartValue(current_rect)
        self.resize_animation.setEndValue(new_rect)
        self.resize_animation.start()
    
    def _send_help_message(self):
        """Send help message to AI"""
        message = self.mini_input.text().strip()
        if not message:
            return
        
        self.mini_input.clear()
        self._add_mini_message("user", message)
        
        # Send to app manager
        self.app_manager.chat_manager.get_help_response(message)
    
    def _send_quick_help(self, message: str):
        """Send quick help message"""
        self._add_mini_message("user", message)
        self.app_manager.chat_manager.get_help_response(message)
    
    def _add_mini_message(self, role: str, content: str):
        """Add message to mini chat"""
        cursor = self.mini_chat.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        if not cursor.atStart():
            cursor.insertText("\n")
        
        if role == "user":
            cursor.insertHtml(f'<span style="color: #87CEEB;">You:</span> {content}')
        else:
            cursor.insertHtml(f'<span style="color: #90EE90;">AI:</span> {content}')
        
        # Scroll to bottom
        scrollbar = self.mini_chat.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot(str, str)
    def _on_message_received(self, role: str, content: str):
        """Handle received message"""
        if role == "assistant":
            self._add_mini_message("assistant", content[:100] + "..." if len(content) > 100 else content)
    
    @pyqtSlot()
    def _on_guidance_paused(self):
        """Handle guidance paused"""
        self._add_mini_message("system", "Guidance paused")
    
    @pyqtSlot()
    def _on_guidance_resumed(self):
        """Handle guidance resumed"""
        self._add_mini_message("system", "Guidance resumed")
    
    def _pause_guidance(self):
        """Pause guidance"""
        self.app_manager.pause_guidance()
    
    def _stop_guidance(self):
        """Stop guidance"""
        self.app_manager.stop_guidance()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.is_dragging = False
    
    def paintEvent(self, event):
        """Custom paint event for rounded corners"""
        # The styling is handled by the frame widgets
        super().paintEvent(event)
        
    def _ensure_visibility(self):
        """Ensure the chat widget remains visible and interactive"""
        if not self.isVisible():
            self.show()
            
        # Make sure it's on top
        self.raise_()
        self.activateWindow()
        
        # If expanded, make sure input field is enabled
        if self.is_expanded:
            self.mini_input.setEnabled(True)
            self.mini_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            # Periodically try to set focus to ensure interactivity
            if not self.mini_input.hasFocus() and self.isActiveWindow():
                self.mini_input.setFocus()
            
        # Check if we're off-screen and reposition if needed
        screen = QApplication.primaryScreen().geometry()
        if not screen.contains(self.geometry()):
            self._position_window()
            
    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.Type.WindowStateChange:
            # If minimized, restore
            if self.windowState() & Qt.WindowState.WindowMinimized:
                self.setWindowState(Qt.WindowState.WindowNoState)
                self.show()
                self.raise_()
                self.activateWindow()
        super().changeEvent(event)