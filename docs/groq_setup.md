# Groq API Setup Guide

This guide will help you set up Groq API for the AI Task Assistant.

## What is Groq?

Groq provides fast inference for various AI models including:
- LLaMA 3 (8B and 70B parameters)
- Mixtral 8x7B
- Gemma 7B
- Claude models

## Step 1: Create a Groq Account

1. Go to [console.groq.com](https://console.groq.com/)
2. Sign up for a free account
3. Verify your email address

## Step 2: Get Your API Key

1. Log in to the Groq console
2. Navigate to the API Keys section
3. Click "Create API Key"
4. Copy your API key (it starts with `gsk_`)

## Step 3: Configure the Application

1. Open the `.env` file in your project root
2. Add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama3-8b-8192
   ```

## Step 4: Test the Connection

1. Run the test script:
   ```bash
   python test_groq.py
   ```
2. Or use the Settings dialog in the app:
   - Open Settings
   - Select "Groq" as the provider
   - Enter your API key
   - Click "Test Connection"

## Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| `llama3-8b-8192` | Fast LLaMA 3 model | General tasks, quick responses |
| `llama3-70b-8192` | Powerful LLaMA 3 model | Complex reasoning, detailed guidance |
| `mixtral-8x7b-32768` | Mixtral with long context | Long conversations, complex tasks |
| `gemma-7b-it` | Google's Gemma model | Instruction following |

## Benefits of Using Groq

- **Fast inference**: Much faster than standard API endpoints
- **Free tier**: Generous free usage limits
- **Multiple models**: Access to various state-of-the-art models
- **Reliable**: High uptime and consistent performance

## Troubleshooting

### "API key not found" error
- Make sure your `.env` file contains `GROQ_API_KEY=your_key_here`
- Restart the application after adding the key

### "Connection test failed" error
- Check your internet connection
- Verify your API key is correct
- Make sure you haven't exceeded rate limits

### "Model not found" error
- Use one of the supported models listed above
- Check the Groq console for available models

## Rate Limits

Groq has generous rate limits for free users:
- Requests per minute: Varies by model
- Tokens per minute: Varies by model
- Check the Groq console for current limits

## Support

If you encounter issues:
1. Check the Groq documentation: [docs.groq.com](https://docs.groq.com/)
2. Visit the Groq community forums
3. Check the application logs for detailed error messages