#!/usr/bin/env python3
"""
Analytics and reporting routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from services.llm_gateway import LLMGateway

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(30, description="Number of days to analyze"),
    user_id: Optional[str] = None
):
    """Get analytics overview"""
    
    try:
        # Mock analytics data - in production, this would query the database
        analytics = {
            "period": {
                "days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "deployments": {
                "total": 142,
                "successful": 135,
                "failed": 7,
                "success_rate": 95.1,
                "average_duration_minutes": 8.5
            },
            "costs": {
                "total_estimated": 4250.50,
                "average_per_deployment": 29.93,
                "total_savings": 8500.25,
                "savings_percentage": 66.7
            },
            "resources": {
                "most_popular": [
                    {"type": "aks", "count": 45, "percentage": 31.7},
                    {"type": "web-server", "count": 38, "percentage": 26.8},
                    {"type": "database", "count": 25, "percentage": 17.6}
                ],
                "cost_tiers": [
                    {"tier": "ultra-low", "count": 85, "percentage": 59.9},
                    {"tier": "low", "count": 35, "percentage": 24.6},
                    {"tier": "medium", "count": 15, "percentage": 10.6}
                ]
            },
            "optimization": {
                "spot_instances_enabled": 127,
                "autoscaling_enabled": 98,
                "average_cost_savings": 1850.75
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/cost-trends")
async def get_cost_trends(
    days: int = Query(30, description="Number of days for trend analysis"),
    granularity: str = Query("daily", description="Granularity: daily, weekly, monthly")
):
    """Get cost trend analysis"""
    
    try:
        # Mock trend data
        trends = {
            "period": days,
            "granularity": granularity,
            "data_points": [
                {
                    "date": "2024-01-15",
                    "total_cost": 125.50,
                    "savings": 300.25,
                    "deployments": 5
                },
                {
                    "date": "2024-01-14",
                    "total_cost": 89.75,
                    "savings": 215.50,
                    "deployments": 3
                },
                {
                    "date": "2024-01-13",
                    "total_cost": 156.25,
                    "savings": 425.75,
                    "deployments": 7
                }
            ],
            "summary": {
                "trend": "decreasing",
                "average_daily_cost": 123.83,
                "total_savings": 941.50,
                "cost_optimization_score": 85.2
            }
        }
        
        return trends
        
    except Exception as e:
        logger.error(f"Error getting cost trends: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cost trends: {str(e)}"
        )


@router.get("/resource-usage")
async def get_resource_usage():
    """Get resource usage statistics"""
    
    try:
        usage_stats = {
            "by_type": [
                {
                    "resource_type": "aks",
                    "total_deployments": 45,
                    "active_instances": 23,
                    "average_cost": 67.50,
                    "total_cost": 1543.50
                },
                {
                    "resource_type": "web-server",
                    "total_deployments": 38,
                    "active_instances": 35,
                    "average_cost": 18.75,
                    "total_cost": 656.25
                },
                {
                    "resource_type": "database",
                    "total_deployments": 25,
                    "active_instances": 18,
                    "average_cost": 45.25,
                    "total_cost": 814.50
                }
            ],
            "by_region": [
                {"region": "eastus", "deployments": 65, "cost": 1956.75},
                {"region": "westus2", "deployments": 35, "cost": 892.50},
                {"region": "centralus", "deployments": 8, "cost": 165.00}
            ],
            "optimization_opportunities": [
                {
                    "type": "unused_resources",
                    "count": 5,
                    "potential_savings": 245.50,
                    "recommendation": "Consider removing idle resources"
                },
                {
                    "type": "oversized_vms",
                    "count": 12,
                    "potential_savings": 456.75,
                    "recommendation": "Downsize to smaller VM SKUs"
                }
            ]
        }
        
        return usage_stats
        
    except Exception as e:
        logger.error(f"Error getting resource usage: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource usage: {str(e)}"
        )


@router.get("/llm-usage")
async def get_llm_usage():
    """Get LLM provider usage statistics"""
    
    try:
        # This would typically come from the LLM gateway
        llm_stats = {
            "total_requests": 1250,
            "total_tokens": 1500000,
            "total_cost": 45.75,
            "providers": [
                {
                    "name": "Google Gemini",
                    "requests": 800,
                    "tokens": 950000,
                    "cost": 0.0,
                    "success_rate": 98.5,
                    "avg_response_time": 1.2
                },
                {
                    "name": "OpenAI GPT-4",
                    "requests": 350,
                    "tokens": 425000,
                    "cost": 35.50,
                    "success_rate": 99.2,
                    "avg_response_time": 2.1
                },
                {
                    "name": "OpenRouter",
                    "requests": 100,
                    "tokens": 125000,
                    "cost": 10.25,
                    "success_rate": 97.8,
                    "avg_response_time": 1.8
                }
            ],
            "cache_stats": {
                "hit_rate": 0.25,
                "total_hits": 312,
                "total_misses": 938,
                "cache_savings": 18.75
            }
        }
        
        return llm_stats
        
    except Exception as e:
        logger.error(f"Error getting LLM usage: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get LLM usage: {str(e)}"
        )


@router.get("/vector-store-stats")
async def get_vector_store_stats():
    """Get vector store statistics"""
    
    try:
        # Mock vector store stats
        vector_stats = {
            "total_templates": 156,
            "embedded_templates": 156,
            "embedding_coverage": 100.0,
            "vector_dimension": 384,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "search_stats": {
                "total_searches": 2450,
                "average_results": 5.2,
                "average_response_time": 0.045,
                "cache_hit_rate": 0.35
            },
            "resource_distribution": {
                "aks": 45,
                "web-server": 38,
                "database": 25,
                "storage": 18,
                "networking": 15,
                "monitoring": 15
            }
        }
        
        return vector_stats
        
    except Exception as e:
        logger.error(f"Error getting vector store stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get vector store stats: {str(e)}"
        )


@router.post("/generate-report")
async def generate_custom_report(
    report_config: Dict[str, Any]
):
    """Generate custom analytics report"""
    
    try:
        # This would typically enqueue a background job to generate the report
        report_id = "report_12345"
        
        return {
            "report_id": report_id,
            "status": "generating",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "config": report_config,
            "download_url": f"/api/v1/analytics/reports/{report_id}/download"
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/reports/{report_id}")
async def get_report_status(report_id: str):
    """Get report generation status"""
    
    try:
        # Mock report status
        return {
            "report_id": report_id,
            "status": "completed",
            "generated_at": datetime.utcnow().isoformat(),
            "size_bytes": 2048576,
            "download_url": f"/api/v1/analytics/reports/{report_id}/download"
        }
        
    except Exception as e:
        logger.error(f"Error getting report status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get report status: {str(e)}"
        )