# Azure AI DevOps Agent - Comprehensive Reference Guide

## Overview

The Azure AI DevOps Agent is an intelligent infrastructure deployment system that automatically finds the cheapest Azure resources, deploys them with real-time progress tracking, and provides personalized usage guides. Built with vector embeddings, multiple LLM providers, and cost optimization algorithms.

## 🚀 Key Features

### Intelligence Layer
- **Vector Embeddings**: Uses ChromaDB + sentence-transformers for semantic resource matching
- **Cost Optimization**: Automatically selects cheapest options with spot instances (60-70% savings)
- **Multiple LLM Providers**: Google Gemini Flash 2.0 (free), Azure OpenAI, Groq, Ollama
- **Real-time Deployment**: Live progress tracking with async generators
- **Post-deployment Guides**: Personalized usage instructions with actual resource details

### User Experience
- **Natural Language Input**: "Create a cheap web server" → Automatic deployment
- **Interactive UI**: Streamlit-based interface with cost intelligence dashboard
- **Quick Actions**: One-click deployment buttons for popular configurations
- **Real-time Feedback**: Progress bars, success animations, resource creation status

## 📁 Project Structure

```
ai-devops-agent/
├── src/                           # Main source code
│   ├── config/                    # Configuration management
│   │   ├── config.py             # Environment and settings
│   │   └── __init__.py
│   ├── database/                  # Vector database & storage
│   │   ├── database.py           # ChromaDB + SQLite integration
│   │   └── __init__.py
│   ├── llm/                      # LLM provider abstraction
│   │   ├── llm_providers.py      # Multi-provider LLM management
│   │   └── __init__.py
│   ├── core/                     # Core business logic
│   │   ├── intelligent_agent.py  # Main AI agent with deployment logic
│   │   ├── azure_resource_manager.py # Azure SDK wrapper
│   │   └── __init__.py
│   ├── agents/                   # Specialized infrastructure agents
│   │   ├── architect_agent.py    # Service mesh & API gateway design
│   │   ├── security_agent.py     # Zero-trust networking & secrets
│   │   ├── cost_agent.py         # Spot instances & autoscaling
│   │   ├── deployment_agent.py   # Blue-green & canary deployments
│   │   ├── monitoring_agent.py   # Prometheus, Grafana, Jaeger
│   │   └── __init__.py
│   ├── ui/                       # User interface
│   │   └── enhanced_streamlit_app.py # Main Streamlit application
│   └── __init__.py
├── templates/                    # Infrastructure templates
│   ├── terraform/               # Terraform configurations
│   ├── kubernetes/              # Kubernetes manifests
│   └── docker/                  # Docker configurations
├── data/                        # Data storage
│   ├── vector_db/              # ChromaDB vector storage
│   └── logs/                   # Application logs
├── scripts/                     # Utility scripts
│   └── setup.py               # Environment setup and validation
├── docs/                       # Documentation
├── tests/                      # Unit and integration tests
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── README.md                  # Project overview
└── CLAUDE.md                  # This comprehensive reference
```

## 🛠️ Quick Start

### 1. Environment Setup
```bash
# Clone and navigate
git clone <repository-url>
cd ai-devops-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and Azure credentials
```

### 2. Required Environment Variables
```bash
# LLM Provider (choose at least one)
GOOGLE_GEMINI_API_KEY=your-google-gemini-api-key  # RECOMMENDED (FREE)
OPENROUTER_API_KEY=your-openrouter-api-key        # Gateway to 100+ models
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-key

# Azure Authentication (REQUIRED)
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-service-principal-client-id
AZURE_CLIENT_SECRET=your-service-principal-secret
```

### 3. Initialize & Run
```bash
# Setup and validate
python scripts/setup.py

# Launch application
streamlit run app.py
```

## 💬 Usage Examples

### Natural Language Interactions
- **"Create a cheap web server"** → Deploys $15/month container instance
- **"Create a development AKS cluster"** → Ultra-low cost AKS with spot instances
- **"Deploy a production-ready Kubernetes cluster"** → Full production AKS setup
- **"I need a database for my app"** → Suggests optimal database options

### Cost Optimization Features
- **Spot Instances**: Automatically enabled for 60-70% cost savings
- **Burstable VMs**: Pay-per-use compute for variable workloads
- **Auto-scaling**: Scales down to minimum nodes when idle
- **Right-sizing**: Matches VM sizes to actual requirements

## 🏗️ Architecture Deep Dive

### Vector Database Integration
```python
# Resource matching using semantic similarity
def find_cheapest_option(self, query: str, resource_type: str = None):
    # Convert query to embedding
    embedding = self.model.encode([query])
    
    # Semantic search in ChromaDB
    results = self.collection.query(
        query_embeddings=embedding,
        n_results=5,
        where={"resource_type": resource_type} if resource_type else {}
    )
    
    # Return cheapest matching template
    return self._select_cheapest_template(results)
```

### Real-time Deployment Tracking
```python
async def execute_deployment_with_feedback(self, template, session_id):
    """Streams deployment progress in real-time"""
    
    yield {"type": "progress", "progress": 15, "message": "Creating prerequisites..."}
    
    # Create resource group
    rg_result = await self.azure_manager.create_resource_group(rg_name, location)
    
    yield {"type": "progress", "progress": 40, "message": f"Creating {template.resource_type}..."}
    
    # Deploy main resource with cost optimizations
    main_result = await self._create_main_resource(template, rg_name)
    
    yield {"type": "success", "progress": 100, "personalized_guide": guide}
```

### Multi-Provider LLM System
```python
class LLMManager:
    def __init__(self):
        self.providers = {
            "google_gemini": GoogleGeminiProvider(),    # FREE
            "groq": GroqProvider(),                     # $0.18/1M tokens
            "azure_openai": AzureOpenAIProvider(),      # $30/1M tokens
            "ollama": OllamaProvider()                  # Local, FREE
        }
        self.fallback_order = ["google_gemini", "ollama", "groq", "azure_openai"]
    
    async def generate_response(self, messages, **kwargs):
        for provider_name in self.fallback_order:
            provider = self.providers[provider_name]
            if provider.is_available():
                try:
                    return await provider.generate_response(messages, **kwargs)
                except Exception as e:
                    continue
        raise Exception("All LLM providers failed")
```

## 🎯 Resource Templates

### Ultra-Low Cost Web Server ($15/month)
```python
ResourceTemplate(
    id="web-ultra-low",
    name="Ultra-Cheap Web Server",
    resource_type="web-server",
    cost_tier="ultra-low",
    monthly_cost_estimate=15.0,
    deployment_time_minutes=5,
    description="Perfect for personal websites, blogs, and small applications",
    configuration={
        "cpu": 0.5,
        "memory": "1.0Gi",
        "enable_spot_instances": True,
        "location": "eastus"
    },
    use_cases=["Personal websites", "Development testing", "Small APIs"]
)
```

### Development AKS Cluster ($45/month)
```python
ResourceTemplate(
    id="aks-ultra-low",
    name="Ultra-Low Cost AKS Cluster",
    resource_type="aks",
    cost_tier="ultra-low", 
    monthly_cost_estimate=45.0,
    deployment_time_minutes=15,
    configuration={
        "node_count": 1,
        "vm_size": "Standard_B2s",
        "enable_spot_instances": True,
        "spot_percentage": 70,
        "enable_autoscaling": True,
        "min_nodes": 1,
        "max_nodes": 3
    }
)
```

## 🔧 Configuration Management

### LLM Provider Priority
1. **Google Gemini Flash 2.0** (Free tier) - Primary choice
2. **Ollama** (Local) - Completely free, requires local setup
3. **OpenRouter** (Gateway) - Access to 100+ models, competitive pricing
4. **Groq** (Very cheap) - $0.18 per 1M tokens, fast inference
5. **Azure OpenAI** (Premium) - Most capable, higher cost

### Cost Optimization Settings
```python
COST_OPTIMIZATIONS = {
    "enable_spot_instances": True,      # 60-70% savings
    "spot_percentage": 70,              # % of spot vs regular nodes
    "enable_autoscaling": True,         # Scale to zero when possible
    "burstable_vms": True,             # Use B-series VMs for variable loads
    "right_sizing": True               # Match VM size to actual needs
}
```

## 📊 Monitoring & Analytics

### Deployment Analytics
- **Success Rate**: Track deployment success across different resource types
- **Cost Trends**: Monitor spending patterns and optimization effectiveness
- **Popular Resources**: Identify most frequently deployed resources
- **Provider Usage**: Track LLM provider costs and performance

### Real-time Dashboards
- **Cost Intelligence**: Potential savings, average costs, cheapest options
- **Provider Comparison**: LLM cost comparison, availability status
- **Deployment History**: Recent deployments with costs and status
- **Resource Usage**: Active resources and their utilization

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# If you get import errors, ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/ai-devops-agent/src"

# Or use the app.py entry point which handles paths automatically
streamlit run app.py
```

#### 2. No LLM Providers Available
```bash
# Check your environment variables
python scripts/setup.py

# For Google Gemini (recommended free option):
# 1. Go to https://makersuite.google.com/app/apikey
# 2. Create API key
# 3. Set GOOGLE_GEMINI_API_KEY in .env
```

#### 3. Azure Authentication Issues
```bash
# Ensure service principal has correct permissions:
# - Contributor role on subscription
# - Owner role for resource group creation
# - Key Vault access for secrets management

# Test Azure login:
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
```

#### 4. Database Initialization Errors
```bash
# Reset vector database
rm -rf data/vector_db/*

# Reinstall ChromaDB
pip uninstall chromadb -y
pip install chromadb==0.4.15

# Reinitialize
python scripts/setup.py
```

## 🧪 Development & Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_database.py
pytest tests/test_llm_providers.py
```

### Adding New Resource Templates
```python
# In src/database/database.py, add to RESOURCE_TEMPLATES:
ResourceTemplate(
    id="my-custom-resource",
    name="My Custom Resource",
    resource_type="custom",
    cost_tier="low",
    monthly_cost_estimate=25.0,
    deployment_time_minutes=8,
    description="Custom resource description",
    configuration={
        # Resource-specific config
    },
    prerequisites=["resource_group"],
    use_cases=["Use case 1", "Use case 2"],
    post_deployment_guide="""
Your custom resource is ready!

Access your resource at: {public_ip}
Resource Group: {rg}
"""
)
```

### Adding New LLM Providers
```python
# Create new provider class in src/llm/llm_providers.py
class MyLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.getenv("MY_LLM_API_KEY")
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_cost_per_token(self) -> Dict[str, float]:
        return {"input": 0.001, "output": 0.002}
    
    async def generate_response(self, messages, **kwargs) -> LLMResponse:
        # Implementation here
        pass

# Add to LLMManager.__init__:
self.providers["my_llm"] = MyLLMProvider()
```

## 📈 Performance Optimization

### Vector Database Performance
- **Batch Operations**: Process multiple templates efficiently
- **Selective Loading**: Load only required embeddings
- **Index Optimization**: Regular HNSW index maintenance
- **Memory Management**: ChromaDB persistence settings

### LLM Provider Optimization
- **Caching**: Cache frequent responses to reduce API calls
- **Token Management**: Optimize prompt sizes for cost efficiency
- **Parallel Processing**: Concurrent LLM requests where possible
- **Fallback Strategy**: Intelligent provider selection based on availability and cost

## 🔐 Security Considerations

### Secrets Management
- **Environment Variables**: Never commit secrets to repository
- **Azure Key Vault**: Integration for production secret storage
- **Service Principals**: Principle of least privilege access
- **API Key Rotation**: Regular rotation of LLM provider keys

### Network Security
- **Zero-Trust Architecture**: Default security posture for all deployments
- **Private Endpoints**: Secure communication between Azure services
- **Network Security Groups**: Restrictive firewall rules
- **RBAC Integration**: Role-based access control for all resources

## 🚀 Production Deployment

### Scaling Considerations
- **Horizontal Scaling**: Multiple Streamlit instances behind load balancer
- **Database Scaling**: Distributed ChromaDB for larger datasets
- **Caching Layer**: Redis for frequently accessed data
- **Monitoring**: Application Performance Monitoring (APM) integration

### CI/CD Pipeline
```yaml
# Example GitHub Actions workflow
name: Deploy Azure AI DevOps Agent
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Deploy to Azure
        run: |
          # Azure deployment commands
```

## 📚 Additional Resources

### Documentation
- [Azure SDK for Python Documentation](https://docs.microsoft.com/en-us/python/api/overview/azure/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)

### Community & Support
- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Community discussions and Q&A
- **Contributing**: Guidelines for contributing to the project

### Changelog & Versions
- **v2.0.0**: Vector embeddings, multi-LLM support, real-time deployment
- **v1.5.0**: Cost optimization, spot instances
- **v1.0.0**: Initial release with basic Azure resource deployment

---

**Last Updated**: January 2025  
**Version**: 2.0.0  
**Compatibility**: Python 3.9+, Azure SDK 2024+