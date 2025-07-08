"""
Chat Widget - Interactive chat interface for AI conversation
Handles the initial conversation phase before guidance starts.
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QScrollArea, QFrame, QLabel)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QPixmap, QPainter

logger = logging.getLogger(__name__)

class ChatWidget(QWidget):
    """Chat interface widget"""
    
    def __init__(self, chat_manager):
        super().__init__()
        
        self.chat_manager = chat_manager
        self.current_task = ""
        
        self._setup_ui()
        self._setup_connections()
        
        # Start chat session
        QTimer.singleShot(500, self._start_chat)
        
        logger.info("ChatWidget initialized")
    
    def _setup_ui(self):
        """Setup chat UI"""
        layout = QVBoxLayout(self)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(400)
        self._style_chat_display()
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self._send_message)
        self.message_input.setMinimumHeight(35)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setMinimumHeight(35)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Typing indicator
        self.typing_indicator = QLabel("AI is typing...")
        self.typing_indicator.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        self.typing_indicator.hide()
        layout.addWidget(self.typing_indicator)
    
    def _style_chat_display(self):
        """Style the chat display area"""
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.chat_manager.message_received.connect(self._on_message_received)
        self.chat_manager.error_occurred.connect(self._on_error)
    
    def _start_chat(self):
        """Start the chat session"""
        self.chat_manager.start_session()
    
    def _send_message(self):
        """Send user message"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Clear input
        self.message_input.clear()
        
        # Add user message to display
        self._add_message("user", message)
        
        # Show typing indicator
        self.typing_indicator.show()
        
        # Send to AI (this will trigger message_received signal)
        QTimer.singleShot(100, lambda: self._send_to_ai(message))
    
    def _send_to_ai(self, message: str):
        """Send message to AI and handle response"""
        try:
            self.chat_manager.send_message(message)
        except Exception as e:
            logger.error(f"Failed to send message to AI: {e}")
            self._on_error(f"Failed to send message: {e}")
        finally:
            self.typing_indicator.hide()
    
    @pyqtSlot(str, str)
    def _on_message_received(self, role: str, content: str):
        """Handle received message"""
        self.typing_indicator.hide()
        self._add_message(role, content)
        
        # Extract task if this looks like a task description
        if role == "user" and len(content) > 20:
            self.current_task = content
    
    @pyqtSlot(str)
    def _on_error(self, error_message: str):
        """Handle error message"""
        self.typing_indicator.hide()
        self._add_message("system", f"Error: {error_message}")
    
    def _add_message(self, role: str, content: str):
        """Add message to chat display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Add some spacing if not first message
        if not cursor.atStart():
            cursor.insertText("\n\n")
        
        # Format message based on role
        if role == "user":
            self._add_user_message(cursor, content)
        elif role == "assistant":
            self._add_assistant_message(cursor, content)
        elif role == "system":
            self._add_system_message(cursor, content)
        
        # Scroll to bottom
        self.chat_display.setTextCursor(cursor)
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _add_user_message(self, cursor: QTextCursor, content: str):
        """Add user message with styling"""
        # User message styling
        cursor.insertHtml(f"""
        <div style="margin-bottom: 10px;">
            <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; 
                       border-top-right-radius: 3px; margin-left: 50px; position: relative;">
                <strong style="color: #1976d2;">You:</strong><br>
                <span style="color: #333;">{self._format_message_content(content)}</span>
            </div>
        </div>
        """)
    
    def _add_assistant_message(self, cursor: QTextCursor, content: str):
        """Add assistant message with styling"""
        # Assistant message styling
        cursor.insertHtml(f"""
        <div style="margin-bottom: 10px;">
            <div style="background-color: #f1f8e9; padding: 10px; border-radius: 10px; 
                       border-top-left-radius: 3px; margin-right: 50px; position: relative;">
                <strong style="color: #388e3c;">🤖 AI Assistant:</strong><br>
                <span style="color: #333;">{self._format_message_content(content)}</span>
            </div>
        </div>
        """)
    
    def _add_system_message(self, cursor: QTextCursor, content: str):
        """Add system message with styling"""
        cursor.insertHtml(f"""
        <div style="margin-bottom: 10px; text-align: center;">
            <div style="background-color: #fff3e0; padding: 8px; border-radius: 6px; 
                       display: inline-block; border: 1px solid #ffcc02;">
                <span style="color: #f57c00; font-size: 12px;">⚠️ {content}</span>
            </div>
        </div>
        """)
    
    def _format_message_content(self, content: str) -> str:
        """Format message content for HTML display"""
        # Escape HTML
        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Convert line breaks
        content = content.replace('\n', '<br>')
        
        # Format bullet points
        content = content.replace('• ', '<br>• ')
        content = content.replace('- ', '<br>• ')
        
        # Format numbered lists
        import re
        content = re.sub(r'^(\d+\.)', r'<br>\1', content, flags=re.MULTILINE)
        
        # Format bold text (markdown style)
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
        
        return content
    
    def get_current_task(self) -> str:
        """Get the current task description"""
        return self.current_task
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.clear()
        self.current_task = ""
        
        # Restart chat session
        QTimer.singleShot(500, self._start_chat)
    
    def add_quick_responses(self, responses: list):
        """Add quick response buttons (for future enhancement)"""
        # This could be implemented to show suggested responses
        pass


class QuickResponseWidget(QWidget):
    """Widget for quick response buttons (future enhancement)"""
    
    def __init__(self, responses: list):
        super().__init__()
        self.responses = responses
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup quick response UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        for response in self.responses:
            btn = QPushButton(response)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border: 1px solid #ccc;
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
            btn.clicked.connect(lambda checked, r=response: self._response_clicked(r))
            layout.addWidget(btn)
        
        layout.addStretch()
    
    def _response_clicked(self, response: str):
        """Handle quick response click"""
        # This would send the response to the chat
        pass