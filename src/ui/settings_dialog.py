"""
Settings Dialog - Configuration interface for the AI Assistant
Allows users to configure API keys, TTS settings, and other preferences.
"""

import os
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QPushButton, QCheckBox, QSpinBox,
                            QComboBox, QLabel, QTabWidget, QWidget, QTextEdit,
                            QGroupBox, QSlider, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings configuration dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("AI Assistant Settings")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self._create_api_tab()
        self._create_detection_tab()
        self._create_tts_tab()
        self._create_ui_tab()
        self._create_about_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test_connection)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Apply styling
        self._apply_styling()
    
    def _create_api_tab(self):
        """Create API configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AI API Group
        ai_group = QGroupBox("AI Configuration")
        ai_layout = QFormLayout(ai_group)
        
        # API Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Groq", "OpenAI", "OpenRouter"])
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        ai_layout.addRow("API Provider:", self.provider_combo)
        
        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your API key here")
        ai_layout.addRow("API Key:", self.api_key_input)
        
        # Base URL input (for OpenRouter or custom endpoints)
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("Leave empty for default API endpoint")
        ai_layout.addRow("Base URL:", self.base_url_input)
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        
        # Default to Groq models
        self._populate_model_dropdown("Groq")
        
        ai_layout.addRow("Model:", self.model_combo)
        
        layout.addWidget(ai_group)
        
        # Backend API Group
        backend_group = QGroupBox("Backend Configuration")
        backend_layout = QFormLayout(backend_group)
        
        self.backend_url_input = QLineEdit()
        self.backend_url_input.setPlaceholderText("http://localhost:8000")
        backend_layout.addRow("Backend URL:", self.backend_url_input)
        
        self.backend_timeout_spin = QSpinBox()
        self.backend_timeout_spin.setRange(5, 60)
        self.backend_timeout_spin.setValue(10)
        self.backend_timeout_spin.setSuffix(" seconds")
        backend_layout.addRow("Timeout:", self.backend_timeout_spin)
        
        layout.addWidget(backend_group)
        
        # Search API Group
        search_group = QGroupBox("Web Search (Optional)")
        search_layout = QFormLayout(search_group)
        
        self.bing_key_input = QLineEdit()
        self.bing_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.bing_key_input.setPlaceholderText("Enter Bing Search API key")
        search_layout.addRow("Bing API Key:", self.bing_key_input)
        
        layout.addWidget(search_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔑 API Keys")
    
    def _create_detection_tab(self):
        """Create detection settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Detection Settings Group
        detection_group = QGroupBox("Screen Detection")
        detection_layout = QFormLayout(detection_group)
        
        self.detection_interval_spin = QSpinBox()
        self.detection_interval_spin.setRange(1, 10)
        self.detection_interval_spin.setValue(2)
        self.detection_interval_spin.setSuffix(" seconds")
        detection_layout.addRow("Detection Interval:", self.detection_interval_spin)
        
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(10, 90)
        self.confidence_slider.setValue(50)
        self.confidence_label = QLabel("50%")
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v}%")
        )
        
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)
        
        detection_layout.addRow("Confidence Threshold:", confidence_layout)
        
        self.max_detections_spin = QSpinBox()
        self.max_detections_spin.setRange(1, 20)
        self.max_detections_spin.setValue(10)
        detection_layout.addRow("Max Detections:", self.max_detections_spin)
        
        layout.addWidget(detection_group)
        
        # Overlay Settings Group
        overlay_group = QGroupBox("Overlay Display")
        overlay_layout = QFormLayout(overlay_group)
        
        self.show_tooltips_check = QCheckBox()
        self.show_tooltips_check.setChecked(True)
        overlay_layout.addRow("Show Tooltips:", self.show_tooltips_check)
        
        self.overlay_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.overlay_opacity_slider.setRange(30, 100)
        self.overlay_opacity_slider.setValue(80)
        self.opacity_label = QLabel("80%")
        self.overlay_opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.overlay_opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        overlay_layout.addRow("Overlay Opacity:", opacity_layout)
        
        layout.addWidget(overlay_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎯 Detection")
    
    def _create_tts_tab(self):
        """Create TTS settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # TTS Settings Group
        tts_group = QGroupBox("Text-to-Speech")
        tts_layout = QFormLayout(tts_group)
        
        self.tts_enabled_check = QCheckBox()
        self.tts_enabled_check.setChecked(True)
        tts_layout.addRow("Enable TTS:", self.tts_enabled_check)
        
        self.tts_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_rate_slider.setRange(100, 300)
        self.tts_rate_slider.setValue(200)
        self.rate_label = QLabel("200 WPM")
        self.tts_rate_slider.valueChanged.connect(
            lambda v: self.rate_label.setText(f"{v} WPM")
        )
        
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(self.tts_rate_slider)
        rate_layout.addWidget(self.rate_label)
        
        tts_layout.addRow("Speech Rate:", rate_layout)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItem("Default Voice", "default")
        # Voice list will be populated when TTS is available
        tts_layout.addRow("Voice:", self.voice_combo)
        
        layout.addWidget(tts_group)
        
        # Test TTS
        test_layout = QHBoxLayout()
        test_text_input = QLineEdit()
        test_text_input.setPlaceholderText("Enter text to test...")
        test_text_input.setText("Hello! This is a test of the text-to-speech system.")
        
        test_tts_btn = QPushButton("Test TTS")
        test_tts_btn.clicked.connect(lambda: self._test_tts(test_text_input.text()))
        
        test_layout.addWidget(test_text_input)
        test_layout.addWidget(test_tts_btn)
        
        layout.addLayout(test_layout)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔊 Speech")
    
    def _create_ui_tab(self):
        """Create UI settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # UI Settings Group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.minimize_to_tray_check = QCheckBox()
        self.minimize_to_tray_check.setChecked(True)
        ui_layout.addRow("Minimize to Tray:", self.minimize_to_tray_check)
        
        self.auto_start_check = QCheckBox()
        self.auto_start_check.setChecked(False)
        ui_layout.addRow("Start with Windows:", self.auto_start_check)
        
        self.show_notifications_check = QCheckBox()
        self.show_notifications_check.setChecked(True)
        ui_layout.addRow("Show Notifications:", self.show_notifications_check)
        
        layout.addWidget(ui_group)
        
        # Theme Settings (future enhancement)
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(theme_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎨 Interface")
    
    def _create_about_tab(self):
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # App info
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <h2>🤖 AI Task Assistant</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> A hybrid AI assistant that guides users through computer tasks using screen detection and conversational AI.</p>
        
        <h3>Features:</h3>
        <ul>
        <li>AI-powered task understanding and guidance</li>
        <li>Real-time screen element detection</li>
        <li>Interactive overlay system</li>
        <li>Text-to-speech assistance</li>
        <li>Floating chat interface</li>
        </ul>
        
        <h3>Technologies:</h3>
        <ul>
        <li>PyQt6 for the user interface</li>
        <li>OpenAI GPT for conversational AI</li>
        <li>Computer vision for screen detection</li>
        <li>Cloud-based ML inference</li>
        </ul>
        
        <h3>Support:</h3>
        <p>For help and support, please refer to the documentation or contact support.</p>
        """)
        
        layout.addWidget(info_text)
        
        self.tab_widget.addTab(tab, "ℹ️ About")
    
    def _apply_styling(self):
        """Apply custom styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QLineEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            
            QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
    
    def _on_provider_changed(self, index):
        """Handle API provider change"""
        provider = self.provider_combo.currentText()
        self._populate_model_dropdown(provider)
        
        # Update placeholder text based on provider
        if provider == "Groq":
            self.api_key_input.setPlaceholderText("Enter your Groq API key")
            self.base_url_input.setText("https://api.groq.com/openai/v1")
            self.base_url_input.setEnabled(False)
        elif provider == "OpenAI":
            self.api_key_input.setPlaceholderText("Enter your OpenAI API key (sk-...)")
            self.base_url_input.setText("")
            self.base_url_input.setEnabled(True)
            self.base_url_input.setPlaceholderText("Leave empty for default OpenAI endpoint")
        elif provider == "OpenRouter":
            self.api_key_input.setPlaceholderText("Enter your OpenRouter API key (sk-or-...)")
            self.base_url_input.setText("https://openrouter.ai/api/v1")
            self.base_url_input.setEnabled(True)
    
    def _populate_model_dropdown(self, provider):
        """Populate model dropdown based on selected provider"""
        self.model_combo.clear()
        
        if provider == "Groq":
            self.model_combo.addItems([
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it",
                "claude-instant-1",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ])
        elif provider == "OpenAI":
            self.model_combo.addItems([
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o"
            ])
        elif provider == "OpenRouter":
            self.model_combo.addItems([
                # Free models
                "google/gemma-2-9b-it:free",
                "anthropic/claude-3-haiku:free",
                "mistralai/mistral-7b-instruct:free",
                "google/gemma-7b-it:free",
                "xai/grok-1:free",
                # Paid models
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "openai/gpt-4",
                "meta-llama/llama-3.1-8b-instruct"
            ])
    
    def _load_settings(self):
        """Load current settings"""
        try:
            # Determine provider based on environment variables
            if os.getenv('GROQ_API_KEY'):
                self.provider_combo.setCurrentText("Groq")
                self.api_key_input.setText(os.getenv('GROQ_API_KEY', ''))
                self.model_combo.setCurrentText(os.getenv('GROQ_MODEL', 'llama3-8b-8192'))
            elif os.getenv('OPENAI_BASE_URL') and 'openrouter' in os.getenv('OPENAI_BASE_URL', ''):
                self.provider_combo.setCurrentText("OpenRouter")
                self.api_key_input.setText(os.getenv('OPENAI_API_KEY', ''))
                self.base_url_input.setText(os.getenv('OPENAI_BASE_URL', ''))
                self.model_combo.setCurrentText(os.getenv('OPENAI_MODEL', 'xai/grok-1:free'))
            else:
                self.provider_combo.setCurrentText("OpenAI")
                self.api_key_input.setText(os.getenv('OPENAI_API_KEY', ''))
                self.base_url_input.setText(os.getenv('OPENAI_BASE_URL', ''))
                self.model_combo.setCurrentText(os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'))
            
            # Other settings
            self.backend_url_input.setText(os.getenv('BACKEND_API_URL', 'http://localhost:8000'))
            self.bing_key_input.setText(os.getenv('BING_SEARCH_API_KEY', ''))
            
            # TTS settings
            tts_enabled = os.getenv('TTS_ENABLED', 'true').lower() == 'true'
            self.tts_enabled_check.setChecked(tts_enabled)
            
            tts_rate = int(os.getenv('TTS_RATE', '200'))
            self.tts_rate_slider.setValue(tts_rate)
            self.rate_label.setText(f"{tts_rate} WPM")
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    def _save_settings(self):
        """Save settings to .env file"""
        try:
            # Prepare settings dictionary based on selected provider
            settings = {}
            provider = self.provider_combo.currentText()
            
            if provider == "Groq":
                settings['GROQ_API_KEY'] = self.api_key_input.text()
                settings['GROQ_MODEL'] = self.model_combo.currentText()
                # Clear other API keys to avoid conflicts
                settings['OPENAI_API_KEY'] = ''
                settings['OPENAI_BASE_URL'] = ''
                settings['OPENAI_MODEL'] = ''
            elif provider == "OpenRouter":
                settings['OPENAI_API_KEY'] = self.api_key_input.text()
                settings['OPENAI_BASE_URL'] = self.base_url_input.text()
                settings['OPENAI_MODEL'] = self.model_combo.currentText()
                # Clear Groq settings
                settings['GROQ_API_KEY'] = ''
                settings['GROQ_MODEL'] = ''
            else:  # OpenAI
                settings['OPENAI_API_KEY'] = self.api_key_input.text()
                settings['OPENAI_BASE_URL'] = self.base_url_input.text() if self.base_url_input.text() else ''
                settings['OPENAI_MODEL'] = self.model_combo.currentText()
                # Clear Groq settings
                settings['GROQ_API_KEY'] = ''
                settings['GROQ_MODEL'] = ''
            
            # Add other settings
            settings.update({
                'BACKEND_API_URL': self.backend_url_input.text(),
                'BING_SEARCH_API_KEY': self.bing_key_input.text(),
                'TTS_ENABLED': 'true' if self.tts_enabled_check.isChecked() else 'false',
                'TTS_RATE': str(self.tts_rate_slider.value()),
                'TTS_VOICE': self.voice_combo.currentData() or 'default'
            })
            
            # Write to .env file
            env_path = '.env'
            with open(env_path, 'w') as f:
                for key, value in settings.items():
                    # Write all values, empty strings will clear the setting
                    f.write(f"{key}={value}\n")
            
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved successfully.\n\nRestart the application for all changes to take effect."
            )
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save settings:\n\n{e}"
            )
    
    def _test_connection(self):
        """Test API connections"""
        try:
            # Get provider and API key
            provider = self.provider_combo.currentText()
            api_key = self.api_key_input.text()
            
            if not api_key:
                QMessageBox.warning(self, "Missing API Key", "Please enter an API key to test the connection.")
                return
                
            import openai
            
            # Setup client based on provider
            if provider == "Groq":
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                model = self.model_combo.currentText() or "llama3-8b-8192"
            elif provider == "OpenRouter":
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                model = self.model_combo.currentText() or "xai/grok-1:free"
            else:  # OpenAI
                # Setup client with base URL if provided
                base_url = self.base_url_input.text()
                if base_url:
                    client = openai.OpenAI(api_key=api_key, base_url=base_url)
                else:
                    client = openai.OpenAI(api_key=api_key)
                model = self.model_combo.currentText() or "gpt-3.5-turbo"
       
            # Simple test request
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello, please respond with a single word."}],
                max_tokens=10
            )
            
            # Show success message
            QMessageBox.information(
                self,
                "Connection Test",
                f"✅ {provider} API connection successful!\nModel: {model}"
            )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection Test",
                f"❌ Connection test failed:\n\n{e}"
            )
    
    def _test_tts(self, text: str):
        """Test TTS functionality"""
        try:
            if not text.strip():
                text = "This is a test of the text-to-speech system."
            
            # This would use the TTS manager
            # For now, just show a message
            QMessageBox.information(
                self,
                "TTS Test",
                f"TTS test would speak: '{text}'\n\n(TTS functionality will be available when the app is running)"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "TTS Test",
                f"TTS test failed:\n\n{e}"
            )