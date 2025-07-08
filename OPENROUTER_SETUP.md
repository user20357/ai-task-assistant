# 🚀 OpenRouter Setup Guide

OpenRouter is a cheaper alternative to OpenAI that provides access to many AI models, including **free models**!

## 📝 Step-by-Step Setup

### 1. Create OpenRouter Account
1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Click "Sign Up" (you can use Google/GitHub)
3. Verify your email

### 2. Get Your API Key
1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Click "Create Key"
3. Give it a name (e.g., "AI Task Assistant")
4. Copy the key (starts with `sk-or-...`)

### 3. Configure the App
1. Open your `.env` file in the project folder
2. Replace `your_openrouter_api_key_here` with your actual key:
   ```
   OPENAI_API_KEY=sk-or-v1-your-actual-key-here
   ```

### 4. Choose Your Model
The app is pre-configured with a **FREE** model: `meta-llama/llama-3.1-8b-instruct:free`

**Free Models Available:**
- `meta-llama/llama-3.1-8b-instruct:free` (recommended)
- `microsoft/phi-3-mini-128k-instruct:free`
- `google/gemma-2-9b-it:free`

**Cheap Paid Models (if you want better performance):**
- `meta-llama/llama-3.1-8b-instruct` (~$0.18/1M tokens)
- `anthropic/claude-3-haiku` (~$0.25/1M tokens)

## 💰 Cost Comparison

**OpenRouter vs OpenAI:**
- OpenAI GPT-3.5: ~$1.50/1M tokens
- OpenRouter Llama 3.1 8B: ~$0.18/1M tokens (8x cheaper!)
- OpenRouter Free Models: $0.00 (completely free!)

## 🧪 Test Your Setup

Run the test script:
```bash
python test_setup.py
```

If everything is configured correctly, you should see:
```
✅ OpenRouter API - OK (Model: meta-llama/llama-3.1-8b-instruct:free)
```

## 🚀 Start the App

Once configured, run:
```bash
python main.py
```

## 🔧 Troubleshooting

**"API key format looks incorrect"**
- Make sure your key starts with `sk-or-`
- Don't include quotes around the key in .env

**"Model not found"**
- Check available models at [https://openrouter.ai/models](https://openrouter.ai/models)
- Free models might have rate limits

**"Rate limit exceeded"**
- Free models have usage limits
- Wait a few minutes or upgrade to a paid model

## 💡 Tips

1. **Start with free models** to test the app
2. **Monitor usage** at [https://openrouter.ai/activity](https://openrouter.ai/activity)
3. **Add credits** if you need higher limits (minimum $5)
4. **Use cheaper models** for basic tasks, better models for complex ones

---

**Ready to go!** Your AI Task Assistant is now configured with affordable AI! 🎉