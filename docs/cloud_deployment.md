# Cloud Deployment Guide

This document explains how the app's cloud components work and how to deploy them.

## Architecture Overview

The app uses a hybrid architecture:

1. **Local Components**:
   - Main UI application
   - YOLO-based detection
   - Overlay rendering
   - Basic UI element detection

2. **Cloud Components**:
   - AI chat service (OpenRouter API)
   - Advanced screen detection API

## Cloud Services Used

### 1. Screen Detection API

- **URL**: https://screensage-backend.onrender.com
- **Purpose**: Advanced screen element detection
- **Hosting**: Render.com (free tier)
- **Technology**: Flask + TensorFlow

### 2. AI Chat Service

- **Provider**: OpenRouter API
- **Models**: Claude 3 Opus / GPT-4
- **Purpose**: Natural language understanding and task guidance

## Deploying Your Own Backend

### Option 1: Deploy on Render.com

1. **Fork the backend repository**:
   ```
   git clone https://github.com/yourusername/screensage-backend.git
   ```

2. **Create a Render.com account** at https://render.com

3. **Create a new Web Service**:
   - Connect your GitHub repository
   - Select Python environment
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn app:app`

4. **Update the API URL** in `src/core/screen_detector.py`

### Option 2: Run Backend Locally

1. **Clone the backend repository**:
   ```
   git clone https://github.com/yourusername/screensage-backend.git
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```
   python app.py
   ```

4. **Update the API URL** in `src/core/screen_detector.py` to `http://localhost:5000`

## Performance Considerations

- The free tier on Render.com has cold starts (30+ seconds delay)
- For production use, consider upgrading to a paid tier
- Alternatively, deploy on AWS, GCP, or Azure for better performance

## Monitoring

- Monitor API usage through the Render.com dashboard
- Set up alerts for high usage or errors
- Check logs for detection accuracy issues