"""
Overlay Manager - Creates transparent overlays on detected screen elements
Shows highlight boxes and instructions over UI elements.
"""

import logging
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                            QFrame, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QObject
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPalette

logger = logging.getLogger(__name__)

class OverlayManager(QObject):
    """Manages screen overlays for detected elements"""
    
    # Signals
    user_clicked_element = pyqtSignal(dict)  # element_info
    
    def __init__(self):
        super().__init__()
        self.active_overlays = {}  # id -> OverlayWidget
        self.instruction_widget = None
        
        logger.info("OverlayManager initialized")
    
    def show_overlays(self, detections: List[Dict[str, Any]], guidance: Any):
        """Show overlays for detected elements"""
        try:
            # Clear existing overlays
            self.hide_all_overlays()
            
            # Handle both string and dict guidance
            if isinstance(guidance, dict):
                instruction = guidance.get('instruction', '')
                priority_elements = guidance.get('priority_elements', detections[:3])
            else:
                # If guidance is a string, use it as instruction
                instruction = str(guidance)
                priority_elements = detections[:5]  # Show top 5 elements
            
            # Show instruction panel
            self._show_instruction_panel(instruction)
            
            # Create overlays for priority elements
            for detection in priority_elements:
                self._create_overlay(detection)
            
            logger.info(f"Showing {len(priority_elements)} overlays")
            
        except Exception as e:
            logger.error(f"Failed to show overlays: {e}")
    
    def _create_overlay(self, detection: Dict[str, Any]):
        """Create overlay widget for a detection"""
        try:
            box = detection['box']
            element_id = detection['id']
            
            # Create overlay widget
            overlay = OverlayWidget(
                detection['label'],
                detection['action'],
                QRect(box[0], box[1], box[2] - box[0], box[3] - box[1]),
                element_id
            )
            
            # Connect click signal
            overlay.element_clicked.connect(self._handle_overlay_click)
            
            # Show overlay
            overlay.show()
            
            # Store reference
            self.active_overlays[element_id] = overlay
            
        except Exception as e:
            logger.error(f"Failed to create overlay: {e}")
    
    def _show_instruction_panel(self, instruction: str):
        """Show floating instruction panel"""
        try:
            if self.instruction_widget:
                self.instruction_widget.close()
            
            self.instruction_widget = InstructionPanel(instruction)
            self.instruction_widget.show()
            
        except Exception as e:
            logger.error(f"Failed to show instruction panel: {e}")
    
    def _handle_overlay_click(self, element_id: str, element_info: Dict[str, Any]):
        """Handle overlay click"""
        try:
            # Hide the clicked overlay
            self.hide_overlay(element_id)
            
            # Emit signal (will be connected by AppManager)
            self.user_clicked_element.emit(element_info)
            
        except Exception as e:
            logger.error(f"Failed to handle overlay click: {e}")
    
    def hide_overlay(self, element_id: str):
        """Hide specific overlay"""
        try:
            if element_id in self.active_overlays:
                overlay = self.active_overlays[element_id]
                overlay.close()
                del self.active_overlays[element_id]
                
        except Exception as e:
            logger.error(f"Failed to hide overlay {element_id}: {e}")
    
    def hide_all_overlays(self):
        """Hide all active overlays"""
        try:
            # Hide all element overlays
            for overlay in self.active_overlays.values():
                overlay.close()
            self.active_overlays.clear()
            
            # Hide instruction panel
            if self.instruction_widget:
                self.instruction_widget.close()
                self.instruction_widget = None
                
        except Exception as e:
            logger.error(f"Failed to hide all overlays: {e}")


class OverlayWidget(QWidget):
    """Individual overlay widget for screen elements"""
    
    element_clicked = pyqtSignal(str, dict)  # element_id, element_info
    
    def __init__(self, label: str, action: str, rect: QRect, element_id: str):
        super().__init__()
        
        self.label = label
        self.action = action
        self.element_rect = rect
        self.element_id = element_id
        
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        """Setup overlay UI"""
        # Window flags for overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Make window transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set geometry to cover the detected element
        margin = 5
        self.setGeometry(
            self.element_rect.x() - margin,
            self.element_rect.y() - margin,
            self.element_rect.width() + 2 * margin,
            self.element_rect.height() + 2 * margin
        )
        
        # Create tooltip label
        self.tooltip_label = QLabel(self.action)
        self.tooltip_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.tooltip_label.setWordWrap(True)
        self.tooltip_label.setMaximumWidth(200)
        
        # Position tooltip above the element
        tooltip_x = max(0, self.element_rect.width() // 2 - 100)
        tooltip_y = -40 if self.element_rect.y() > 50 else self.element_rect.height() + 10
        
        self.tooltip_label.move(tooltip_x, tooltip_y)
        self.tooltip_label.setParent(self)
    
    def _setup_animation(self):
        """Setup pulsing animation"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_pulse)
        self.animation_timer.start(1000)  # Pulse every second
        
        self.pulse_opacity = 1.0
        self.pulse_direction = -0.1
    
    def _animate_pulse(self):
        """Animate pulsing effect"""
        self.pulse_opacity += self.pulse_direction
        
        if self.pulse_opacity <= 0.3:
            self.pulse_direction = 0.1
        elif self.pulse_opacity >= 1.0:
            self.pulse_direction = -0.1
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the overlay"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw highlight box
        pen = QPen(QColor(255, 0, 0, int(255 * self.pulse_opacity)))    # RED
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Draw rectangle around the element
        margin = 5
        rect = QRect(margin, margin, 
                    self.element_rect.width(), 
                    self.element_rect.height())
        painter.drawRect(rect)
        
        # Draw corner indicators
        corner_size = 10
        brush = QBrush(QColor(255, 0, 0, int(200 * self.pulse_opacity)))  # RED
        painter.setBrush(brush)
        
        # Top-left corner
        painter.drawRect(margin, margin, corner_size, corner_size)
        # Top-right corner
        painter.drawRect(rect.right() - corner_size, margin, corner_size, corner_size)
        # Bottom-left corner
        painter.drawRect(margin, rect.bottom() - corner_size, corner_size, corner_size)
        # Bottom-right corner
        painter.drawRect(rect.right() - corner_size, rect.bottom() - corner_size, corner_size, corner_size)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            element_info = {
                'id': self.element_id,
                'label': self.label,
                'action': self.action,
                'rect': [self.element_rect.x(), self.element_rect.y(), 
                        self.element_rect.width(), self.element_rect.height()]
            }
            self.element_clicked.emit(self.element_id, element_info)
    
    def closeEvent(self, event):
        """Cleanup when closing"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        super().closeEvent(event)


class InstructionPanel(QWidget):
    """Floating instruction panel"""
    
    def __init__(self, instruction: str):
        super().__init__()
        
        self.instruction = instruction
        self._setup_ui()
        self._position_panel()
    
    def _setup_ui(self):
        """Setup instruction panel UI"""
        # Window flags - make sure it's interactive and visible
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Ensure the widget accepts focus and mouse events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        
        # Styling - make it more visible with brighter colors
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 250);
                border-radius: 12px;
                border: 3px solid #FF5722;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 16px;
            }
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF7043;
            }
        """)
        
        # Layout
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("NEXT STEP:")
        title_label.setStyleSheet("color: #FF9800; font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Instruction text with RED SQUARES mention
        instruction_text = self.instruction
        if "RED" not in instruction_text and "red" not in instruction_text:
            instruction_text = f"Look for the RED SQUARES and {instruction_text}"
            
        instruction_label = QLabel(instruction_text)
        instruction_label.setWordWrap(True)
        instruction_label.setMinimumWidth(400)
        instruction_label.setMinimumHeight(100)
        layout.addWidget(instruction_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        got_it_btn = QPushButton("Got it!")
        got_it_btn.clicked.connect(self.close)
        button_layout.addWidget(got_it_btn)
        
        help_btn = QPushButton("Need Help")
        help_btn.clicked.connect(self._request_help)
        button_layout.addWidget(help_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _position_panel(self):
        """Position panel on screen"""
        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        
        # Position at center-top of screen for better visibility
        self.adjustSize()
        x = (screen.width() - self.width()) // 2
        y = 50
        
        self.move(x, y)
        
        # Make sure it's visible and on top
        self.raise_()
        self.activateWindow()
    
    def _request_help(self):
        """Request help from AI"""
        # This would be connected to the chat system
        # For now, just close the panel
        self.close()