# 🚀 Azure AI DevOps Agent

**Intelligent infrastructure deployment with cost optimization and real-time feedback**

Transform natural language requests like "create a cheap web server" into fully deployed Azure resources with automatic cost optimization and personalized usage guides.

## ✨ Key Features

- 🧠 **Vector Embeddings**: Semantic resource matching with ChromaDB
- 💰 **Cost Optimization**: Automatic spot instances (60-70% savings)
- 🤖 **Multiple LLM Providers**: Google Gemini Flash 2.0 (free), OpenRouter (100+ models), Azure OpenAI, Groq, Ollama
- ⚡ **Real-time Deployment**: Live progress tracking with async feedback
- 📖 **Personalized Guides**: Post-deployment instructions with actual resource details
- 🎯 **Natural Language**: "Create a cheap AKS cluster" → Automatic deployment

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd ai-devops-agent
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (Google Gemini recommended for free tier)

# 3. Initialize and run
python scripts/setup.py
streamlit run app.py
```

## 💬 Try These Commands

- **"Create a cheap web server for $15/month"**
- **"Deploy a development AKS cluster"**
- **"Create an ultra-low cost production environment"**

## 📊 Cost Intelligence

| Resource Type | Ultra-Low Cost | Savings |
|---------------|----------------|---------|
| Web Server | $15/month | 75% |
| AKS Dev Cluster | $45/month | 65% |
| Production AKS | $150/month | 60% |

## 🏗️ Architecture

```
📁 Project Structure
├── src/
│   ├── config/          # Environment & settings
│   ├── database/        # Vector DB & storage
│   ├── llm/             # Multi-provider LLM system
│   ├── core/            # AI agent & Azure integration
│   ├── agents/          # Specialized infrastructure agents
│   └── ui/              # Streamlit interface
├── templates/           # Infrastructure as code
├── data/                # Vector embeddings & logs
└── scripts/             # Setup & utilities
```

## 🔧 Configuration

**Required:** Azure subscription credentials  
**Recommended:** Google Gemini API key (free tier) or OpenRouter API key  
**Optional:** Azure OpenAI, Groq, or Ollama for additional LLM options

## 📚 Documentation

- **[CLAUDE.md](./CLAUDE.md)** - Comprehensive reference guide
- **[Setup Guide](./scripts/setup.py)** - Environment validation
- **[Architecture Deep Dive](./CLAUDE.md#architecture-deep-dive)** - Technical details

## 🎯 Use Cases

- **Development**: Ultra-cheap dev environments with spot instances
- **Production**: Cost-optimized production deployments
- **Learning**: Hands-on Azure learning with real-time feedback
- **Experimentation**: Quick resource prototyping and testing

---

**Built with Intelligence** • Vector embeddings • Cost optimization • Real-time feedback • Multiple LLM providers