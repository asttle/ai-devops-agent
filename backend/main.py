#!/usr/bin/env python3
"""
FastAPI Backend for AI DevOps Agent
Simplified version with Context7 MCP and multi-cloud support
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from core.config import get_settings, validate_environment
from api.routes import infrastructure, health, analytics
from services.llm_gateway import LLMGateway

# Configure structured logging
logger = structlog.get_logger(__name__)

def create_app() -> FastAPI:
    """Create FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="AI DevOps Agent API",
        description="AI-powered cloud infrastructure platform with Context7 MCP",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize LLM Gateway
    app.state.llm_gateway = LLMGateway()
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(infrastructure.router, prefix="/api/v1/infrastructure", tags=["infrastructure"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "AI DevOps Agent API",
            "version": "2.0.0",
            "status": "operational",
            "features": {
                "documentation": "Context7 MCP",
                "web_framework": "FastAPI + Hono",
                "cloud_providers": ["AWS", "Azure", "GCP"],
                "ai_framework": "Web Search + LLM"
            },
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "infrastructure": "/api/v1/infrastructure",
                "analytics": "/api/v1/analytics"
            }
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    try:
        validate_environment()
        logger.info("Environment validation successful")
    except Exception as e:
        logger.warning(f"Environment validation issues: {e}")
    
    logger.info("Starting AI DevOps Agent API")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )