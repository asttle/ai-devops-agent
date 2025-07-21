# OpenRouter Gateway Setup Guide

OpenRouter is an LLM gateway that provides access to 100+ AI models through a single API, offering competitive pricing and excellent model variety.

## 🌟 Why OpenRouter?

- **100+ Models**: Access Claude, GPT-4, Llama, Gemini, and more through one API
- **Competitive Pricing**: Often cheaper than direct provider access
- **Free Models**: Access to free Llama 3.1 and other open-source models
- **Unified API**: OpenAI-compatible API for easy integration
- **Credits System**: Pay-as-you-go with $5 minimum credit purchase

## 🚀 Quick Setup

### 1. Get OpenRouter API Key
1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for an account
3. Purchase credits (minimum $5)
4. Go to [Keys](https://openrouter.ai/keys) and create an API key
5. Copy your API key

### 2. Configure Environment
Add to your `.env` file:
```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free  # Free model!
OPENROUTER_APP_NAME=Azure AI DevOps Agent
OPENROUTER_SITE_URL=https://github.com/your-username/azure-ai-devops-agent
```

## 🎯 Recommended Models

### Free Models (No cost)
```bash
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free    # Free Llama 3.1
OPENROUTER_MODEL=google/gemini-flash-1.5                   # Free Gemini Flash
```

### Ultra-Cheap Models (< $0.001/1K tokens)
```bash
OPENROUTER_MODEL=anthropic/claude-3-haiku:beta             # $0.25/1M input
OPENROUTER_MODEL=openai/gpt-3.5-turbo                     # $0.5/1M input
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct        # $0.4/1M input
```

### High-Quality Models (Best performance)
```bash
OPENROUTER_MODEL=anthropic/claude-3-sonnet:beta           # $3/1M input
OPENROUTER_MODEL=openai/gpt-4-turbo                       # $10/1M input
OPENROUTER_MODEL=anthropic/claude-3-opus:beta             # $15/1M input
```

## 💰 Cost Optimization

### Smart Model Selection
```bash
# Development/Testing: Use free models
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free

# Production: Use balanced cost/quality
OPENROUTER_MODEL=anthropic/claude-3-haiku:beta

# Complex tasks: Use premium models selectively
OPENROUTER_MODEL=anthropic/claude-3-sonnet:beta
```

### Credit Management
- **Monitor Usage**: Check your credit balance at [OpenRouter Dashboard](https://openrouter.ai/activity)
- **Set Limits**: Configure spending limits to avoid overuse
- **Model Fallbacks**: Our system automatically falls back to cheaper models if needed

## 🔧 Advanced Configuration

### Custom Headers
```bash
# Optional: Customize your app identification
OPENROUTER_APP_NAME=My Custom Azure DevOps Agent
OPENROUTER_SITE_URL=https://mycompany.com/devops-agent
```

### Rate Limits
OpenRouter handles rate limiting automatically with intelligent queuing.

## 🎛️ Model Categories

### Code Generation
- `codellama/codellama-70b-instruct` - Specialized for code
- `anthropic/claude-3-haiku:beta` - Fast and good for simple code tasks

### General Intelligence
- `anthropic/claude-3-sonnet:beta` - Excellent balance of speed/quality
- `openai/gpt-4-turbo` - OpenAI's flagship model

### Cost-Optimized
- `meta-llama/llama-3.1-8b-instruct:free` - Completely free
- `google/gemini-flash-1.5` - Fast and cheap

### Reasoning & Analysis
- `anthropic/claude-3-opus:beta` - Best for complex reasoning
- `openai/o1-preview` - Advanced reasoning capabilities

## 📊 Pricing Comparison

| Model | Input ($/1M) | Output ($/1M) | Use Case |
|-------|--------------|---------------|----------|
| Llama 3.1 8B Free | $0.00 | $0.00 | Development/Testing |
| Claude 3 Haiku | $0.25 | $1.25 | General tasks |
| GPT-3.5 Turbo | $0.50 | $1.50 | Balanced performance |
| Claude 3 Sonnet | $3.00 | $15.00 | Complex tasks |
| GPT-4 Turbo | $10.00 | $30.00 | Premium performance |

## 🚨 Best Practices

### Development
```bash
# Use free models for development
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

### Production
```bash
# Use cost-effective models with good performance
OPENROUTER_MODEL=anthropic/claude-3-haiku:beta
```

### Fallback Strategy
The system automatically tries models in this order:
1. Google Gemini (if configured) - Free
2. OpenRouter with your configured model
3. Other configured providers

## 🔍 Troubleshooting

### Common Issues

**1. "Insufficient Credits"**
```bash
# Check your credit balance at https://openrouter.ai/activity
# Purchase more credits or switch to a free model
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

**2. "Model Not Available"**
```bash
# Check model availability at https://openrouter.ai/models
# Some models may have temporary availability issues
```

**3. "Rate Limited"**
OpenRouter handles this automatically with intelligent queuing. If persistent, consider:
- Using a less popular model
- Spreading requests over time
- Upgrading to a higher credit tier

### Testing Your Setup
```bash
# Test your OpenRouter configuration
python scripts/setup.py

# Should show:
# ✅ 1 LLM provider(s) available:
#   - openrouter (meta-llama/llama-3.1-8b-instruct:free) (FREE)
```

## 🎯 Integration Example

The OpenRouter provider is automatically integrated. Once configured, you can:

1. **Chat Interface**: Just start chatting - OpenRouter will be used automatically
2. **Model Selection**: The system picks the best available model based on your configuration
3. **Cost Tracking**: All costs are tracked and displayed in the dashboard

## 📈 Advanced Features

### Dynamic Model Selection
```python
# The system can switch models based on task complexity
# Simple tasks: Free models
# Complex deployments: Premium models
```

### Usage Analytics
- Track spending by model
- Monitor token usage
- Optimize model selection based on cost/performance

---

**OpenRouter provides an excellent balance of cost, performance, and model variety for the Azure AI DevOps Agent!**