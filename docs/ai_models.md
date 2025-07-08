# AI Models Integration

This document explains how the AI Task Assistant integrates with various AI models, including Grok AI and other models via Groq.

## Supported AI Models

The application supports multiple AI models through direct API integrations:

1. **Groq API Models**
   - LLaMA 3 (8B and 70B)
   - Mixtral 8x7B
   - Gemma 7B
   - Claude Instant
   - Claude 3 Opus/Sonnet/Haiku

2. **OpenAI GPT Models**
   - GPT-4
   - GPT-3.5 Turbo

3. **OpenRouter Models** (alternative integration)
   - All OpenAI models
   - Anthropic Claude models
   - Google Gemma models
   - xAI Grok-1
   - Many others

## Using Groq API (Recommended)

Groq provides fast access to multiple high-quality models:

1. **Set up Groq**
   - Create an account at [console.groq.com](https://console.groq.com/)
   - Get your API key from the console

2. **Configure Environment Variables**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama3-8b-8192
   ```

3. **Available Groq Models**
   - `llama3-8b-8192`: Fast, efficient LLaMA 3 model
   - `llama3-70b-8192`: More powerful LLaMA 3 model
   - `mixtral-8x7b-32768`: Mixtral model with long context
   - `gemma-7b-it`: Google's Gemma model
   - `claude-instant-1`: Fast Claude model
   - `claude-3-opus-20240229`: Most powerful Claude model
   - `claude-3-sonnet-20240229`: Balanced Claude model
   - `claude-3-haiku-20240307`: Fast Claude model

## AI Task Planning

The application uses AI to generate detailed task plans:

1. **Task Analysis**
   - When the user describes a task, the AI analyzes it
   - The AI identifies the necessary steps to complete the task

2. **Step Generation**
   - Each step includes:
     - Action (click, type, drag, etc.)
     - Target UI element
     - Description
     - Expected result

3. **Dynamic Guidance**
   - The AI matches detected screen elements to the current step
   - It guides the user by highlighting relevant elements with RED SQUARES
   - It adapts if the user deviates from the expected path

## Customizing AI Behavior

You can customize how the AI generates guidance:

1. **Adjust Prompts**
   - Edit the system prompts in `src/core/ai_chat.py`
   - Modify the task planning prompt to change how steps are generated

2. **Change Models**
   - Different models have different strengths
   - Grok is good for technical tasks
   - Claude is good for detailed explanations
   - GPT-4 is good for general-purpose guidance

3. **Adjust Parameters**
   - Temperature: Lower for more consistent guidance, higher for creativity
   - Max tokens: Adjust based on how detailed you want the guidance to be