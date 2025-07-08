"""
Main Window - Primary interface for the AI Assistant
Handles initial chat and task setup before switching to guidance mode.
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QLineEdit, QPushButton, QLabel, 
                            QSplitter, QFrame, QScrollArea, QMessageBox,
                            QSystemTrayIcon, QMenu, QApplication)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QAction

from .chat_widget import ChatWidget
from .floating_chat import FloatingChatWidget
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, app_manager):
        super().__init__()
        
        self.app_manager = app_manager
        self.floating_chat = None
        self.tray_icon = None
        
        self._setup_ui()
        self._setup_connections()
        self._setup_system_tray()
        
        logger.info("MainWindow initialized")
    
    def _setup_ui(self):
        """Setup main window UI"""
        self.setWindowTitle("AI Task Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Set window icon
        self._create_app_icon()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header
        self._create_header(layout)
        
        # Chat area
        self.chat_widget = ChatWidget(self.app_manager.chat_manager)
        layout.addWidget(self.chat_widget)
        
        # Control buttons
        self._create_control_buttons(layout)
        
        # Status bar
        self.statusBar().showMessage("Ready - Start by describing your task")
        
        # Apply styling
        self._apply_styling()
    
    def _create_app_icon(self):
        """Create application icon"""
        # Create a simple icon programmatically
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a simple AI assistant icon
        painter.setBrush(Qt.GlobalColor.blue)
        painter.drawEllipse(4, 4, 24, 24)
        
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(8, 8, 4, 4)  # Left eye
        painter.drawEllipse(20, 8, 4, 4)  # Right eye
        painter.drawEllipse(12, 16, 8, 4)  # Mouth
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.setWindowIcon(icon)
        
        return icon
    
    def _create_header(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setMaximumHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title and description
        title_layout = QVBoxLayout()
        
        title_label = QLabel("🤖 AI Task Assistant")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        desc_label = QLabel("I'll help you complete computer tasks step-by-step")
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #666;")
        title_layout.addWidget(desc_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self._show_settings)
        header_layout.addWidget(settings_btn)
        
        layout.addWidget(header_frame)
    
    def _create_control_buttons(self, layout):
        """Create control buttons"""
        button_layout = QHBoxLayout()
        
        # Start Guidance button
        self.start_btn = QPushButton("🎯 Start Guidance")
        self.start_btn.setEnabled(False)  # Enabled when task is ready
        self.start_btn.clicked.connect(self._start_guidance)
        self.start_btn.setMinimumHeight(40)
        button_layout.addWidget(self.start_btn)
        
        # Force Start button (always available)
        self.force_start_btn = QPushButton("🚀 Force Start")
        self.force_start_btn.setToolTip("Start guidance even if task detection didn't work")
        self.force_start_btn.clicked.connect(self._force_start_guidance)
        self.force_start_btn.setMinimumHeight(40)
        button_layout.addWidget(self.force_start_btn)
        
        # Clear Chat button
        clear_btn = QPushButton("🗑️ Clear Chat")
        clear_btn.clicked.connect(self._clear_chat)
        button_layout.addWidget(clear_btn)
        
        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Setup signal connections"""
        # App manager connections
        self.app_manager.task_ready.connect(self._on_task_ready)
        self.app_manager.task_started.connect(self._on_task_started)
        self.app_manager.task_completed.connect(self._on_task_completed)
        self.app_manager.error_occurred.connect(self._on_error)
        
        # Chat manager connections
        self.app_manager.chat_manager.message_received.connect(self._on_message_received)
    
    def _setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.windowIcon())
            
            # Tray menu
            tray_menu = QMenu()
            
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(QApplication.quit)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self._tray_icon_activated)
            
            self.tray_icon.show()
    
    def _apply_styling(self):
        """Apply custom styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QPushButton#start_btn {
                background-color: #2196F3;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#start_btn:hover {
                background-color: #1976D2;
            }
            
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            
            QStatusBar {
                background-color: #e0e0e0;
                border-top: 1px solid #ccc;
            }
        """)
        
        # Set start button object name for styling
        self.start_btn.setObjectName("start_btn")
    
    @pyqtSlot(str)
    def _on_task_ready(self, task_description: str):
        """Handle task ready signal"""
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🎯 Start Guidance - Ready!")
        self.statusBar().showMessage(f"Task ready: {task_description[:50]}... Click 'Start Guidance' to begin!")
    
    @pyqtSlot(str, str)
    def _on_message_received(self, role: str, content: str):
        """Handle new chat message"""
        # The chat widget handles this directly
        pass
    
    @pyqtSlot(str)
    def _on_task_started(self, task_description: str):
        """Handle task started signal"""
        # Switch to floating mode
        self._switch_to_floating_mode()
        self.statusBar().showMessage(f"Guidance active: {task_description}")
    
    @pyqtSlot()
    def _on_task_completed(self):
        """Handle task completed signal"""
        # Switch back to normal mode
        self._switch_to_normal_mode()
        self.statusBar().showMessage("Task completed - Ready for new task")
        
        # Reset buttons
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🎯 Start Guidance")
        self.force_start_btn.setEnabled(True)
        self.force_start_btn.setText("🚀 Force Start")
        
        # Show completion message
        QMessageBox.information(
            self,
            "Task Completed",
            "Great job! Your task has been completed successfully.\n\nYou can start a new task anytime."
        )
    
    @pyqtSlot(str)
    def _on_error(self, error_message: str):
        """Handle error signal"""
        logger.error(f"App error: {error_message}")
        self.statusBar().showMessage(f"Error: {error_message}")
        
        QMessageBox.warning(
            self,
            "Error",
            f"An error occurred:\n\n{error_message}"
        )
    
    def _start_guidance(self):
        """Start guidance mode"""
        try:
            # Get task description from chat
            task_desc = self.chat_widget.get_current_task()
            if not task_desc:
                task_desc = "User task"
            
            # Start guidance through app manager
            self.app_manager.start_guidance(task_desc)
            self._update_guidance_ui_active()
            
        except Exception as e:
            logger.error(f"Failed to start guidance: {e}")
            self._on_error(f"Failed to start guidance: {e}")
    
    def _force_start_guidance(self):
        """Force start guidance even without proper task detection"""
        try:
            # Get the last user message as task description
            chat_history = getattr(self.app_manager.chat_manager, 'conversation_history', [])
            user_messages = [msg['content'] for msg in chat_history if msg['role'] == 'user']
            
            if user_messages:
                task_description = user_messages[-1]  # Use last user message
            else:
                task_description = "General computer task assistance"
            
            # Set current task
            self.app_manager.chat_manager.current_task = task_description
            
            # Start guidance
            self.app_manager.start_guidance(task_description)
            self._update_guidance_ui_active()
            
            # Show info
            QMessageBox.information(
                self, 
                "🎯 Visual Guidance Started!", 
                f"Task: {task_description[:100]}...\n\n✅ RED squares will highlight clickable elements\n✅ YOLO AI will detect icons (Chrome, close buttons, etc.)\n✅ Follow the step-by-step instructions\n\nThe main window will now minimize to a floating chat."
            )
            
        except Exception as e:
            logger.error(f"Failed to force start guidance: {e}")
            self._on_error(f"Failed to start guidance: {e}")
    
    def _update_guidance_ui_active(self):
        """Update UI when guidance becomes active"""
        self.start_btn.setEnabled(False)
        self.start_btn.setText("🎯 Guidance Active")
        self.force_start_btn.setEnabled(False)
        self.force_start_btn.setText("🎯 Active")
        self.statusBar().showMessage("Guidance mode active - Follow the highlighted elements")
    
    def _switch_to_floating_mode(self):
        """Switch to floating chat mode"""
        try:
            # Hide main window
            self.hide()
            
            # Create floating chat if not exists
            if not self.floating_chat:
                self.floating_chat = FloatingChatWidget(self.app_manager)
            
            # Show floating chat
            self.floating_chat.show()
            
        except Exception as e:
            logger.error(f"Failed to switch to floating mode: {e}")
    
    def _switch_to_normal_mode(self):
        """Switch back to normal mode"""
        try:
            # Hide floating chat
            if self.floating_chat:
                self.floating_chat.hide()
            
            # Show main window
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Reset start button
            self.start_btn.setEnabled(False)
            self.start_btn.setText("🎯 Start Guidance")
            
        except Exception as e:
            logger.error(f"Failed to switch to normal mode: {e}")
    
    def _clear_chat(self):
        """Clear chat history"""
        reply = QMessageBox.question(
            self,
            "Clear Chat",
            "Are you sure you want to clear the chat history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_widget.clear_chat()
            self.start_btn.setEnabled(False)
            self.start_btn.setText("🎯 Start Guidance")
            self.statusBar().showMessage("Chat cleared - Ready for new task")
    
    def _show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
        <h3>AI Task Assistant Help</h3>
        
        <p><b>How to use:</b></p>
        <ol>
        <li>Describe the task you want to accomplish</li>
        <li>Answer the AI's questions about prerequisites</li>
        <li>Click "Start Guidance" when ready</li>
        <li>Follow the on-screen highlights and instructions</li>
        </ol>
        
        <p><b>During guidance:</b></p>
        <ul>
        <li>Orange boxes highlight clickable elements</li>
        <li>Use the floating chat to ask questions</li>
        <li>Say "pause" to pause guidance</li>
        <li>Say "stop" to end guidance</li>
        </ul>
        
        <p><b>Tips:</b></p>
        <ul>
        <li>Be specific about your task</li>
        <li>Have required files/accounts ready</li>
        <li>Ask for help if you get stuck</li>
        </ul>
        """
        
        QMessageBox.information(self, "Help", help_text)
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        # Convert reason to int to avoid C++ object conversion issues
        reason_int = int(reason)
        
        # DoubleClick is typically value 2
        if reason_int == 2:  # QSystemTrayIcon.ActivationReason.DoubleClick
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Ask user if they want to close or minimize
        if not hasattr(self, '_close_confirmed'):
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Close Application")
            msg_box.setText("Do you want to close the application or minimize it?")
            minimize_btn = msg_box.addButton("Minimize", QMessageBox.ButtonRole.ActionRole)
            close_btn = msg_box.addButton("Close", QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.exec()
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == close_btn:
                # Actually close
                self._close_confirmed = True
                self.app_manager.cleanup()
                event.accept()
            elif clicked_button == minimize_btn:
                # Minimize to taskbar
                self.showMinimized()
                event.ignore()
            else:
                # Cancel
                event.ignore()
        else:
            # User already confirmed closing
            self.app_manager.cleanup()
            event.accept()