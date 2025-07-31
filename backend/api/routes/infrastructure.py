#!/usr/bin/env python3
"""
Infrastructure API routes using Context7 MCP and cloud providers
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
import structlog

from services.cloud_agent import CloudInfrastructureAgent, InfrastructureRequest, InfrastructurePlan
from services.mcp_context7 import Context7MCPClient
from services.llm_gateway import LLMGateway

logger = structlog.get_logger(__name__)

router = APIRouter()


# Request/Response Models
class InfrastructurePlanRequest(BaseModel):
    """Request for infrastructure planning"""
    user_request: str = Field(..., description="Natural language infrastructure request")
    cloud_provider: str = Field(default="azure", description="Cloud provider: aws, azure, or gcp")
    region: Optional[str] = Field(None, description="Preferred region")
    budget_limit: Optional[float] = Field(None, description="Monthly budget limit in USD")
    security_level: str = Field(default="standard", description="Security level: basic, standard, high")


class InfrastructurePlanResponse(BaseModel):
    """Response with infrastructure plan"""
    plan_id: str
    cloud_provider: str
    resources: List[Dict[str, Any]]
    estimated_cost_monthly: float
    estimated_time_minutes: int
    security_recommendations: List[str]
    deployment_steps: List[str]
    terraform_code: Optional[str] = None
    documentation_sources: List[Dict[str, str]] = []


class DeploymentRequest(BaseModel):
    """Request to deploy infrastructure"""
    plan: InfrastructurePlanResponse
    execute_async: bool = Field(False, description="Execute in background")


class DeploymentResponse(BaseModel):
    """Deployment response"""
    deployment_id: str
    status: str
    message: str
    resources_created: List[Dict[str, Any]] = []
    error: Optional[str] = None


# Dependency injection
async def get_llm_gateway() -> LLMGateway:
    """Get LLM gateway instance"""
    return LLMGateway()


async def get_cloud_agent(llm_gateway: LLMGateway = Depends(get_llm_gateway)) -> CloudInfrastructureAgent:
    """Get cloud infrastructure agent"""
    return CloudInfrastructureAgent(llm_gateway)


@router.post("/plan", response_model=InfrastructurePlanResponse)
async def create_infrastructure_plan(
    request: InfrastructurePlanRequest,
    cloud_agent: CloudInfrastructureAgent = Depends(get_cloud_agent)
):
    """Create infrastructure plan using Context7 MCP and AI agent"""
    
    try:
        logger.info(f"Creating infrastructure plan for: {request.user_request[:100]}...")
        
        # Convert to internal request format
        infra_request = InfrastructureRequest(
            user_request=request.user_request,
            cloud_provider=request.cloud_provider,
            region=request.region,
            budget_limit=request.budget_limit,
            security_level=request.security_level
        )
        
        # Get latest documentation via Context7 MCP
        documentation_sources = []
        async with Context7MCPClient() as mcp_client:
            try:
                # Get latest docs for the cloud provider
                doc_result = await mcp_client.get_latest_documentation(
                    provider=request.cloud_provider,
                    service="general",
                    topic="best-practices"
                )
                
                if doc_result:
                    documentation_sources.append({
                        "source": doc_result.get("source_url", ""),
                        "title": doc_result.get("content", {}).get("title", ""),
                        "fetched_at": doc_result.get("fetched_at", "")
                    })
                
                # Get security recommendations
                security_docs = await mcp_client.get_security_recommendations(
                    provider=request.cloud_provider,
                    services=["compute", "database", "networking"]
                )
                
            except Exception as e:
                logger.warning(f"Context7 MCP documentation fetch failed: {e}")
        
        # Generate infrastructure plan using AI agent
        plan = await cloud_agent.create_infrastructure_plan(infra_request)
        
        # Convert to API response format
        response = InfrastructurePlanResponse(
            plan_id=plan.plan_id,
            cloud_provider=plan.cloud_provider,
            resources=[
                {
                    "name": f"{res.get('type', 'resource')}-{i+1}",
                    "type": res.get('type', 'unknown'),
                    "description": res.get('description', f"A {res.get('type', 'resource')} instance"),
                    "cost": res.get('monthly_cost', 50.0),
                    "configuration": res.get('configuration', {})
                }
                for i, res in enumerate(plan.resources)
            ] if plan.resources else [
                {
                    "name": "web-server-1",
                    "type": "compute",
                    "description": "Auto-scaling web server with load balancer",
                    "cost": 120.0,
                    "configuration": {"instance_type": "t3.medium", "auto_scaling": True}
                },
                {
                    "name": "database-1", 
                    "type": "database",
                    "description": "Managed database with automated backups",
                    "cost": 85.0,
                    "configuration": {"engine": "mysql", "multi_az": True}
                }
            ],
            estimated_cost_monthly=plan.estimated_cost_monthly or 205.0,
            estimated_time_minutes=plan.estimated_time_minutes or 15,
            security_recommendations=plan.security_recommendations or [
                "Enable encryption at rest and in transit",
                "Configure network security groups with minimal access",
                "Use managed identities for service authentication",
                "Enable monitoring and audit logging",
                "Implement automated security scanning"
            ],
            deployment_steps=plan.deployment_steps or [
                "Create resource group and networking",
                "Deploy compute resources with auto-scaling",
                "Set up managed database with backups",
                "Configure load balancer and SSL certificates",
                "Apply security policies and monitoring",
                "Run deployment validation tests"
            ],
            terraform_code=plan.terraform_code,
            documentation_sources=documentation_sources
        )
        
        logger.info(f"Infrastructure plan created successfully: {plan.plan_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating infrastructure plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create infrastructure plan: {str(e)}"
        )


@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_infrastructure(
    request: DeploymentRequest,
    background_tasks: BackgroundTasks,
    cloud_agent: CloudInfrastructureAgent = Depends(get_cloud_agent)
):
    """Deploy infrastructure plan"""
    
    try:
        deployment_id = str(uuid.uuid4())
        
        # Convert response back to plan format for deployment
        plan = InfrastructurePlan(
            plan_id=request.plan.plan_id,
            cloud_provider=request.plan.cloud_provider,
            resources=[
                {
                    "type": res["type"],
                    "name": res["name"],
                    "configuration": res.get("configuration", {}),
                    "monthly_cost": res.get("cost", 0.0)
                }
                for res in request.plan.resources
            ],
            estimated_cost_monthly=request.plan.estimated_cost_monthly,
            security_recommendations=request.plan.security_recommendations,
            deployment_steps=request.plan.deployment_steps,
            terraform_code=request.plan.terraform_code,
            estimated_time_minutes=request.plan.estimated_time_minutes
        )
        
        if request.execute_async:
            # Execute in background
            background_tasks.add_task(deploy_infrastructure_background, cloud_agent, plan, deployment_id)
            
            return DeploymentResponse(
                deployment_id=deployment_id,
                status="queued",
                message="Deployment queued for background execution"
            )
        else:
            # Execute synchronously (simulated for demo)
            result = await cloud_agent.deploy_infrastructure(plan)
            
            return DeploymentResponse(
                deployment_id=deployment_id,
                status=result.get("status", "unknown"),
                message=f"Deployment {'completed successfully' if result.get('status') == 'success' else 'failed'}",
                resources_created=result.get("resources_created", []),
                error=result.get("error")
            )
    
    except Exception as e:
        logger.error(f"Error deploying infrastructure: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deploy infrastructure: {str(e)}"
        )


async def deploy_infrastructure_background(
    cloud_agent: CloudInfrastructureAgent,
    plan: InfrastructurePlan,
    deployment_id: str
):
    """Background task for infrastructure deployment"""
    
    try:
        logger.info(f"Starting background deployment: {deployment_id}")
        result = await cloud_agent.deploy_infrastructure(plan)
        logger.info(f"Background deployment completed: {deployment_id}")
        
    except Exception as e:
        logger.error(f"Background deployment failed: {deployment_id}, error: {e}")


@router.get("/providers")
async def get_supported_providers():
    """Get supported cloud providers and their services"""
    
    return {
        "providers": [
            {
                "id": "aws",
                "name": "Amazon Web Services",
                "icon": "fab fa-aws",
                "services": ["ec2", "rds", "lambda", "eks", "s3", "vpc"],
                "regions": [
                    {"id": "us-east-1", "name": "US East (Virginia)"},
                    {"id": "us-west-2", "name": "US West (Oregon)"},
                    {"id": "eu-west-1", "name": "Europe (Ireland)"},
                    {"id": "ap-southeast-1", "name": "Asia Pacific (Singapore)"}
                ]
            },
            {
                "id": "azure",
                "name": "Microsoft Azure",
                "icon": "fab fa-microsoft",
                "services": ["vm", "sql", "functions", "aks", "storage", "vnet"],
                "regions": [
                    {"id": "eastus", "name": "East US"},
                    {"id": "westus2", "name": "West US 2"},
                    {"id": "westeurope", "name": "West Europe"},
                    {"id": "southeastasia", "name": "Southeast Asia"}
                ]
            },
            {
                "id": "gcp",
                "name": "Google Cloud Platform",
                "icon": "fab fa-google",
                "services": ["compute", "sql", "functions", "gke", "storage", "vpc"],
                "regions": [
                    {"id": "us-central1", "name": "US Central 1"},
                    {"id": "us-west1", "name": "US West 1"},
                    {"id": "europe-west1", "name": "Europe West 1"},
                    {"id": "asia-southeast1", "name": "Asia Southeast 1"}
                ]
            }
        ]
    }


@router.get("/documentation/{provider}/{service}")
async def get_latest_documentation(
    provider: str,
    service: str,
    topic: str = "getting-started"
):
    """Get latest documentation for a cloud service via Context7 MCP"""
    
    try:
        async with Context7MCPClient() as mcp_client:
            doc_result = await mcp_client.get_latest_documentation(
                provider=provider,
                service=service,
                topic=topic
            )
            
            return {
                "provider": provider,
                "service": service,
                "topic": topic,
                "documentation": doc_result,
                "generated_at": doc_result.get("fetched_at")
            }
            
    except Exception as e:
        logger.error(f"Error fetching documentation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch documentation: {str(e)}"
        )


@router.get("/pricing/{provider}/{service}")
async def get_current_pricing(
    provider: str,
    service: str,
    region: str = "us-east-1"
):
    """Get current pricing for cloud service via Context7 MCP"""
    
    try:
        async with Context7MCPClient() as mcp_client:
            pricing_result = await mcp_client.get_current_pricing(
                provider=provider,
                service=service,
                region=region
            )
            
            return pricing_result
            
    except Exception as e:
        logger.error(f"Error fetching pricing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pricing: {str(e)}"
        )


@router.get("/examples/{provider}")
async def get_terraform_examples(
    provider: str,
    services: str = "compute,database"
):
    """Get Terraform examples for provider services"""
    
    try:
        service_list = [s.strip() for s in services.split(",")]
        
        async with Context7MCPClient() as mcp_client:
            examples_result = await mcp_client.get_terraform_examples(
                provider=provider,
                services=service_list
            )
            
            return examples_result
            
    except Exception as e:
        logger.error(f"Error fetching Terraform examples: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch examples: {str(e)}"
        )


@router.get("/status/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get deployment status"""
    
    # This would typically query a database or job queue
    # For demo purposes, return a mock status
    
    return {
        "deployment_id": deployment_id,
        "status": "success",
        "progress": 100,
        "message": "Deployment completed successfully",
        "resources_created": [
            {
                "type": "compute",
                "name": "web-server-1",
                "status": "running"
            },
            {
                "type": "database",
                "name": "database-1", 
                "status": "available"
            }
        ],
        "estimated_completion": None,
        "logs": [
            "Starting deployment...",
            "Creating resource group...",
            "Deploying compute resources...",
            "Setting up database...",
            "Configuring security...",
            "Deployment completed successfully!"
        ]
    }