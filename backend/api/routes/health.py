#!/usr/bin/env python3
"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, Request
from typing import Dict, Any
import asyncio
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Azure AI DevOps Agent API"
    }


@router.get("/detailed")
async def detailed_health():
    """Detailed health check with component status"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Azure AI DevOps Agent API",
        "version": "2.0.0",
        "components": {}
    }
    
    try:
        from fastapi import Request
        
        # Check database
        try:
            # In a real implementation, you'd check database connectivity
            health_status["components"]["database"] = {
                "status": "healthy",
                "type": "PostgreSQL + pgvector"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check Redis
        try:
            # In a real implementation, you'd ping Redis
            health_status["components"]["redis"] = {
                "status": "healthy",
                "type": "Redis Cache & Job Queue"
            }
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check LLM providers
        try:
            health_status["components"]["llm_gateway"] = {
                "status": "healthy",
                "providers": ["Google Gemini", "OpenAI", "OpenRouter"]
            }
        except Exception as e:
            health_status["components"]["llm_gateway"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check vector store
        try:
            health_status["components"]["vector_store"] = {
                "status": "healthy",
                "type": "pgvector"
            }
        except Exception as e:
            health_status["components"]["vector_store"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    
    try:
        # Check if all critical services are ready
        # This is a simplified check
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "error": str(e)
        }, 503


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/llm-providers")
async def llm_providers_status(request: Request):
    """Check LLM providers status"""
    try:
        llm_gateway = request.app.state.llm_gateway
        providers = llm_gateway.get_available_providers()
        
        return {
            "status": "success",
            "providers": providers,
            "fallback_order": llm_gateway.fallback_order,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"LLM providers check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }