# 🤖 AI Task Assistant

A hybrid Windows application that guides users through computer tasks step-by-step using AI chat and real-time screen detection with overlay highlights.

## ✨ Features

- **AI-Powered Chat**: Conversational AI that understands your tasks and asks clarifying questions
- **Screen Detection**: Real-time detection of UI elements (buttons, text, icons) using computer vision
- **Interactive Overlays**: Highlight boxes that show exactly where to click
- **Floating Chat**: Minimized chat interface during guidance mode
- **Text-to-Speech**: Optional voice guidance and explanations
- **Task Breakdown**: AI breaks down complex tasks into simple steps
- **Web Search Integration**: AI can search for task-specific information

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **OpenAI API Key** (get from [OpenAI](https://platform.openai.com/api-keys))
3. **Windows 10/11** (primary target platform)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aiv2
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-your-api-key-here
     ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## 🎯 How to Use

### Step 1: Describe Your Task
- Launch the app and describe what you want to accomplish
- Examples: "Upload my resume to a job portal", "Fill out a government form", "Search for information online"

### Step 2: Answer AI Questions
- The AI will ask about prerequisites (accounts, files, software needed)
- Be specific about your requirements and available resources

### Step 3: Start Guidance
- Click "Start Guidance" when the AI confirms everything is ready
- The main window minimizes to a floating chat box

### Step 4: Follow the Highlights
- RED SQUARES will highlight clickable elements on your screen
- Instructions appear at the top of your screen
- Use the floating chat to ask questions anytime

### Step 5: Complete Your Task
- Follow the step-by-step guidance
- Ask for help if you get stuck
- The AI adapts to your progress

## 🛠️ Backend Setup (Optional)

For enhanced screen detection, you can run the backend API:

### Local Backend

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend**:
   ```bash
   python main.py
   ```

The backend will run on `http://localhost:8000`

### Cloud Deployment (Render.com)

1. **Create a new Web Service** on Render.com
2. **Connect your GitHub repository**
3. **Set build command**: `pip install -r backend/requirements.txt`
4. **Set start command**: `cd backend && python main.py`
5. **Update your `.env` file** with the deployed URL:
   ```
   BACKEND_API_URL=https://your-app.onrender.com
   ```

## ⚙️ Configuration

### Settings Dialog
Access via the "Settings" button in the main window:

- **API Keys**: Configure OpenAI and Bing Search APIs
- **Detection**: Adjust detection interval and confidence
- **Speech**: Configure text-to-speech settings
- **Interface**: Customize UI preferences

### Environment Variables
Configure in `.env` file:

```bash
# AI API - Choose ONE of these options:

# Option 1: Groq API (Recommended for LLaMA 3 and other models)
# See docs/groq_setup.md for detailed setup instructions
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-8b-8192

# Option 2: OpenAI API
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-3.5-turbo

# Other settings
BACKEND_API_URL=http://localhost:8000
BING_SEARCH_API_KEY=your-bing-key
TTS_ENABLED=true
TTS_RATE=200
```

## 🏗️ Architecture

### Frontend (PyQt6)
- **Main Window**: Initial chat and task setup
- **Chat Widget**: AI conversation interface
- **Floating Chat**: Minimized guidance interface
- **Overlay Manager**: Screen highlight system
- **Screen Detector**: Computer vision integration

### Backend (FastAPI)
- **Detection API**: Screen element detection
- **OCR Integration**: Text recognition
- **Computer Vision**: UI pattern detection

### AI Integration
- **Groq API Support**: Fast access to LLaMA 3, Mixtral, and Claude models
- **Task Planning**: AI generates detailed step-by-step plans
- **Visual Guidance**: AI identifies UI elements to click with RED SQUARES
- **Context Awareness**: Adapts to user progress and screen state

## 🔧 Development

### Project Structure
```
aiv2/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── src/
│   ├── core/              # Core application logic
│   │   ├── app_manager.py # Central coordinator
│   │   ├── ai_chat.py     # AI conversation manager
│   │   ├── screen_detector.py # Screen detection
│   │   ├── overlay_manager.py # Overlay system
│   │   └── tts_manager.py # Text-to-speech
│   └── ui/                # User interface
│       ├── main_window.py # Main application window
│       ├── chat_widget.py # Chat interface
│       ├── floating_chat.py # Floating chat
│       └── settings_dialog.py # Settings
└── backend/               # Detection API
    ├── main.py           # FastAPI server
    └── requirements.txt  # Backend dependencies
```

### Adding New Features

1. **New Detection Types**: Extend `screen_detector.py`
2. **UI Enhancements**: Modify components in `src/ui/`
3. **AI Capabilities**: Enhance `ai_chat.py`
4. **Backend Models**: Add to `backend/main.py`

## 🚨 Troubleshooting

### Common Issues

**"OpenAI API Error"**
- Check your API key in Settings
- Ensure you have API credits
- Verify internet connection

**"Screen Detection Not Working"**
- Check backend URL in Settings
- Ensure backend is running
- Try local detection fallback

**"Overlays Not Showing"**
- Check Windows permissions
- Disable fullscreen applications
- Adjust overlay opacity in Settings

**"TTS Not Working"**
- Enable TTS in Settings
- Check Windows speech settings
- Try different voice options

**"Application Hangs or Crashes"**
- Wait for the timeout recovery (10 seconds)
- Click anywhere on screen to continue
- Minimize and restore the application
- Restart the application if needed

### Performance Tips

- **Reduce detection interval** for slower computers
- **Lower confidence threshold** for more detections
- **Disable TTS** if not needed
- **Use local backend** for faster response

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT API
- **PyQt6** for the UI framework
- **OpenCV** for computer vision
- **EasyOCR** for text recognition
- **FastAPI** for the backend API

## 📞 Support

For help and support:
- Check the troubleshooting section
- Review the configuration guide
- Open an issue on GitHub

---

**Happy task automation!** 🎉