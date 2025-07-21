#!/usr/bin/env python3
"""
Configuration management for Azure AI DevOps Agent
Handles environment variables, Azure credentials, and application settings
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, ChainedTokenCredential, AzureCliCredential, ManagedIdentityCredential
from dataclasses import dataclass

# Load environment variables
load_dotenv()

@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration"""
    endpoint: str
    api_key: str
    api_version: str = "2024-02-01"
    deployment_name: str = "gpt-4"
    
    @classmethod
    def from_env(cls) -> 'AzureOpenAIConfig':
        return cls(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        )
    
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key)

@dataclass
class AzureConfig:
    """Azure configuration"""
    subscription_id: str
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    default_location: str = "eastus"
    default_resource_group_prefix: str = "rg-ai-devops"
    default_cluster_name_prefix: str = "aks-cluster"
    
    @classmethod
    def from_env(cls) -> 'AzureConfig':
        return cls(
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID", ""),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            default_location=os.getenv("DEFAULT_LOCATION", "eastus"),
            default_resource_group_prefix=os.getenv("DEFAULT_RESOURCE_GROUP_PREFIX", "rg-ai-devops"),
            default_cluster_name_prefix=os.getenv("DEFAULT_CLUSTER_NAME_PREFIX", "aks-cluster")
        )
    
    def get_credential(self) -> DefaultAzureCredential:
        """Get Azure credential using the credential chain"""
        try:
            # Try different credential types in order
            credential_chain = ChainedTokenCredential(
                ManagedIdentityCredential(),  # For Azure VM/App Service
                AzureCliCredential(),         # For local development with Azure CLI
                DefaultAzureCredential()      # Fallback to default chain
            )
            return credential_chain
        except Exception as e:
            logging.warning(f"Failed to create credential chain, using DefaultAzureCredential: {e}")
            return DefaultAzureCredential()

@dataclass
class DevOpsConfig:
    """DevOps configuration"""
    azure_devops_org_url: Optional[str] = None
    azure_devops_pat: Optional[str] = None
    github_token: Optional[str] = None
    github_username: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'DevOpsConfig':
        return cls(
            azure_devops_org_url=os.getenv("AZURE_DEVOPS_ORG_URL"),
            azure_devops_pat=os.getenv("AZURE_DEVOPS_PAT"),
            github_token=os.getenv("GITHUB_TOKEN"),
            github_username=os.getenv("GITHUB_USERNAME")
        )

@dataclass
class AppConfig:
    """Application configuration"""
    log_level: str = "INFO"
    streamlit_theme: str = "dark"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            streamlit_theme=os.getenv("STREAMLIT_THEME", "dark"),
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )

class Config:
    """Main configuration class that aggregates all config sections"""
    
    def __init__(self):
        self.azure_openai = AzureOpenAIConfig.from_env()
        self.azure = AzureConfig.from_env()
        self.devops = DevOpsConfig.from_env()
        self.app = AppConfig.from_env()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.app.log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('ai_devops_agent.log')
            ]
        )
    
    def validate_required_config(self) -> Dict[str, bool]:
        """Validate that required configuration is present"""
        validation = {
            "azure_openai_configured": self.azure_openai.is_configured(),
            "azure_subscription_configured": bool(self.azure.subscription_id),
            "azure_credentials_available": self._test_azure_credentials()
        }
        return validation
    
    def _test_azure_credentials(self) -> bool:
        """Test if Azure credentials are working"""
        try:
            credential = self.azure.get_credential()
            # Try to get a token to validate credentials
            token = credential.get_token("https://management.azure.com/.default")
            return bool(token.token)
        except Exception as e:
            logging.warning(f"Azure credentials test failed: {e}")
            return False
    
    def get_azure_openai_client(self):
        """Get configured Azure OpenAI client"""
        try:
            import openai
            
            client = openai.AzureOpenAI(
                azure_endpoint=self.azure_openai.endpoint,
                api_key=self.azure_openai.api_key,
                api_version=self.azure_openai.api_version
            )
            return client
        except Exception as e:
            logging.error(f"Failed to create Azure OpenAI client: {e}")
            return None
    
    def get_resource_tags(self, additional_tags: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get standard resource tags"""
        tags = {
            "CreatedBy": "AI-DevOps-Agent",
            "Environment": "Production",
            "Project": "AKS-Infrastructure",
            "ManagedBy": "Automation"
        }
        
        if additional_tags:
            tags.update(additional_tags)
        
        return tags

# Global config instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def validate_environment() -> bool:
    """Validate that the environment is properly configured"""
    validation = config.validate_required_config()
    
    all_valid = all(validation.values())
    
    if not all_valid:
        logging.error("Environment validation failed:")
        for check, result in validation.items():
            if not result:
                logging.error(f"  ❌ {check}")
            else:
                logging.info(f"  ✅ {check}")
    else:
        logging.info("Environment validation passed!")
    
    return all_valid

if __name__ == "__main__":
    # Test configuration when run directly
    print("Testing configuration...")
    validate_environment()
    
    print(f"Azure Subscription ID: {config.azure.subscription_id}")
    print(f"Default Location: {config.azure.default_location}")
    print(f"Azure OpenAI Configured: {config.azure_openai.is_configured()}")