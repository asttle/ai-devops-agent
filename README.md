# 🤖 AI DevOps Agent v2.0

> **Intelligent Cloud Infrastructure Assistant powered by Pydantic AI, Context7 MCP, and Hono Framework**

Transform natural language requests into production-ready cloud infrastructure with real-time documentation, cost optimization, and multi-cloud support.

## ✨ Key Features

### 🧠 **Advanced AI Framework**
- **Pydantic AI** for intelligent agent operations
- **Context7 MCP** for real-time documentation access
- **Web Search Integration** for current best practices
- **Multi-LLM Support** with cost optimization

### ☁️ **Multi-Cloud Support**
- **AWS, Azure, GCP** native SDK integration
- **Real-time pricing** and cost optimization
- **Infrastructure as Code** (Terraform) generation
- **Security best practices** enforcement

### 🚀 **Modern Architecture**
- **Hono Framework** for blazing-fast frontend
- **FastAPI** backend with async support
- **No RAG complexity** - uses web search for current info
- **Production-ready** with monitoring and security

## 🎯 Why This Approach?

### ❌ **What We Removed (From PoC)**
- **RAG/Vector Database** - Unnecessary for public documentation
- **Complex ChromaDB setup** - Web search is more current
- **Heavy authentication** - Simplified for focus on core features
- **Streamlit limitations** - Replaced with modern Hono framework

### ✅ **What We Added (Production Ready)**
- **Real-time documentation** via Context7 MCP
- **Web search integration** for latest best practices
- **Multi-cloud SDK support** for actual deployments
- **Modern web framework** with Hono
- **Cost optimization focus** with spot instances, etc.

## 🚀 Quick Start

### 1. **Prerequisites**
```bash
# Required
- Python 3.9+
- uv (Python package manager) - https://docs.astral.sh/uv/
- Node.js 18+
- Git

# API Keys (at least one LLM provider)
- Google Gemini API key (recommended - free tier)
- Azure credentials (for Azure deployments)
```

### 2. **Installation**
```bash
# Clone repository
git clone <your-repo-url>
cd ai-devops-agent

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # Add your GOOGLE_GEMINI_API_KEY and Azure credentials

# Install dependencies with uv
uv sync
```

### 3. **Start Development Environment**
```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Start backend
uv run python backend/main.py

# In another terminal, start frontend
cd frontend && npm install && npm run dev
```

This will start:
- **Backend** (FastAPI): http://localhost:8000
- **Frontend** (Hono): http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### 4. **Access the Application**
Open your browser to **http://localhost:3000** and start building infrastructure!

## 💡 Example Usage

### Natural Language to Infrastructure

**Input:**
> "I need a scalable e-commerce platform that can handle Black Friday traffic with global CDN, auto-scaling web servers, managed database with read replicas, Redis caching, and comprehensive monitoring. Budget around $2000/month."

**Output:**
- Detailed infrastructure plan with cost estimates
- Security recommendations from latest documentation
- Terraform code for deployment
- Step-by-step deployment guide

### Quick Examples Available
- **Scalable Web Application** - Load balancer, auto-scaling, database
- **Microservices Platform** - Kubernetes, service mesh, API gateway
- **Data Processing Pipeline** - Data warehouse, ETL, analytics
- **ML/AI Platform** - Training, serving, MLOps pipeline

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Hono Frontend │───▶│  FastAPI Backend │───▶│  Cloud Providers│
│   (Port 3000)   │    │   (Port 8000)    │    │   AWS/Azure/GCP │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Interface│    │  Pydantic AI    │    │  Real Resources │
│   • Modern UI   │    │  • Context7 MCP │    │  • Live Pricing │
│   • Real-time   │    │  • Web Search   │    │  • Terraform    │
│   • Responsive  │    │  • LiteLLM      │    │  • Monitoring   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend (Hono Framework)
- **Hono** - Ultra-fast web framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Modern styling
- **Alpine.js** - Reactive components

### Backend (FastAPI + Pydantic AI)
- **FastAPI** - High-performance API framework
- **Pydantic AI** - Advanced AI agent framework
- **Context7 MCP** - Real-time documentation access
- **LiteLLM** - Unified LLM provider gateway

### AI & Documentation
- **Web Search** - Current best practices (no stale RAG data)
- **Context7 MCP** - Latest cloud provider documentation
- **Multiple LLM Providers** - Gemini (free), OpenAI, Azure OpenAI
- **Cost Optimization** - Automatic cheapest provider selection

### Cloud Integration
- **Native SDKs** - Direct integration with AWS, Azure, GCP
- **Real-time Pricing** - Live cost estimates
- **Infrastructure as Code** - Terraform generation
- **Security Focus** - Latest security recommendations

## 📊 Key Improvements Over PoC

| Feature | PoC (Before) | Production (Now) | Benefit |
|---------|--------------|------------------|---------|
| **Documentation** | Static RAG | Context7 MCP + Web Search | Always current info |
| **Frontend** | Streamlit | Hono Framework | Modern, fast, scalable |
| **AI Framework** | Basic LLM calls | Pydantic AI | Advanced reasoning |
| **Cloud Providers** | Limited Azure | AWS + Azure + GCP | Multi-cloud flexibility |
| **Information Source** | Vector database | Real-time web search | Latest best practices |
| **Cost Focus** | Basic templates | Live pricing + optimization | Real cost savings |

## 🔧 Configuration

### Environment Variables

#### Required
```bash
# LLM Provider (choose at least one)
GOOGLE_GEMINI_API_KEY=your_key_here  # Recommended (free)
OPENAI_API_KEY=your_key_here         # Alternative

# Cloud Provider (for deployments)
AZURE_SUBSCRIPTION_ID=your_sub_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_secret
```

#### Optional
```bash
# Additional LLM providers
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
OPENROUTER_API_KEY=your_openrouter_key

# AWS (if using AWS deployments)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Application settings
DEBUG=true
LOG_LEVEL=INFO
```

## 🌟 Why This Approach is Better

### 1. **No RAG Complexity**
- **Problem**: RAG with vector databases adds complexity and can have stale data
- **Solution**: Real-time web search + Context7 MCP for always-current information

### 2. **Real-time Documentation**
- **Problem**: Documentation changes frequently, vector databases get outdated
- **Solution**: Context7 MCP fetches latest docs directly from providers

### 3. **Modern Frontend**
- **Problem**: Streamlit is limited for complex UIs
- **Solution**: Hono framework provides modern, fast, scalable web interface

### 4. **Multi-Cloud Reality**
- **Problem**: Organizations use multiple cloud providers
- **Solution**: Native SDK integration for AWS, Azure, and GCP

### 5. **Cost Optimization Focus**
- **Problem**: Cloud costs are a major concern
- **Solution**: Real-time pricing, spot instances, and cost-optimized recommendations

## 🔍 API Endpoints

### Infrastructure Management
- `POST /api/v1/infrastructure/plan` - Generate infrastructure plan
- `POST /api/v1/infrastructure/deploy` - Deploy infrastructure
- `GET /api/v1/infrastructure/providers` - List supported providers

### Documentation & Pricing
- `GET /api/v1/infrastructure/documentation/{provider}/{service}` - Latest docs
- `GET /api/v1/infrastructure/pricing/{provider}/{service}` - Current pricing
- `GET /api/v1/infrastructure/examples/{provider}` - Terraform examples

### System
- `GET /health` - Health check
- `GET /docs` - API documentation
- `GET /metrics` - Prometheus metrics

## 🚢 Production Deployment

### Docker (Recommended)
```bash
# Build and run
docker-compose up -d

# Or use production compose
docker-compose -f docker-compose.production.yml up -d
```

### Manual Deployment
```bash
# Backend
uv sync --frozen
uv run python backend/main.py

# Frontend
cd frontend
npm install
npm run build
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check `/docs` endpoint when running
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

---

**🚀 Ready to transform your infrastructure management with AI?**

Start with: `./start-dev.sh` and visit http://localhost:3000

**Built with ❤️ using Pydantic AI, Context7 MCP, and Hono Framework**