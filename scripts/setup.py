#!/usr/bin/env python3
"""
Setup script for Azure AI DevOps Agent
Initializes database, validates configuration, and prepares the environment
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_environment():
    """Validate environment variables"""
    required_vars = [
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_TENANT_ID", 
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please copy .env.example to .env and configure your values")
        return False
    
    print("✅ All required environment variables are set")
    return True

def initialize_database():
    """Initialize the vector database"""
    try:
        from database import get_database
        db = get_database()
        db.initialize_templates()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def check_llm_providers():
    """Check available LLM providers"""
    try:
        from llm import get_llm_manager
        llm_manager = get_llm_manager()
        providers = llm_manager.get_available_providers()
        
        if not providers:
            print("⚠️  No LLM providers available. Please configure at least one:")
            print("  - Google Gemini (Free): Set GOOGLE_GEMINI_API_KEY")
            print("  - OpenRouter (Gateway): Set OPENROUTER_API_KEY")
            print("  - Azure OpenAI: Set AZURE_OPENAI_* variables") 
            print("  - Groq (Cheap): Set GROQ_API_KEY")
            print("  - Ollama (Local): Install Ollama locally")
            return False
        
        print(f"✅ {len(providers)} LLM provider(s) available:")
        for provider in providers:
            free_badge = " (FREE)" if provider["free"] else f" (${provider['cost_per_1k_input']:.3f}/1K)"
            print(f"  - {provider['name']} ({provider['model']}){free_badge}")
        
        return True
    except Exception as e:
        print(f"❌ LLM provider check failed: {e}")
        return False

def main():
    """Main setup function"""
    setup_logging()
    print("🚀 Azure AI DevOps Agent - Setup")
    print("=" * 50)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    success = True
    
    # Validate environment
    print("\n📋 Validating environment...")
    success &= validate_environment()
    
    # Initialize database
    print("\n💾 Initializing database...")  
    success &= initialize_database()
    
    # Check LLM providers
    print("\n🤖 Checking LLM providers...")
    success &= check_llm_providers()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Setup completed successfully!")
        print("Run: streamlit run app.py")
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()