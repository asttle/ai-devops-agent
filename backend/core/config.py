#!/usr/bin/env python3
"""
Simple configuration management
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    app_name: str = "AI DevOps Agent"
    version: str = "2.0.0"
    debug: bool = False
    
    # Security
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # LLM Providers
    google_gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    # Azure
    azure_subscription_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    
    # AWS
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_default_region: str = "us-east-1"
    
    # GCP
    gcp_project_id: Optional[str] = None
    google_application_credentials: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def validate_environment():
    """Validate required environment variables"""
    settings = get_settings()
    
    # Check for at least one LLM provider
    llm_providers = [
        settings.google_gemini_api_key,
        settings.openai_api_key,
        settings.azure_openai_api_key,
        settings.openrouter_api_key
    ]
    
    if not any(llm_providers):
        raise ValueError("At least one LLM provider API key must be configured")
    
    return True