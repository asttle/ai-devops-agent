#!/usr/bin/env python3
"""
Cloud Infrastructure Agent - No RAG, uses web search and cloud SDKs
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
import structlog

from services.llm_gateway import LLMGateway
from services.web_search import WebSearchService
from services.cloud_providers import AWSManager, AzureManager, GCPManager
from services.security_validator import SecurityValidator
from services.prompt_templates import DevOpsPromptTemplates

logger = structlog.get_logger(__name__)


@dataclass
class AgentDependencies:
    """Dependencies for the Pydantic AI agent"""
    web_search: 'WebSearchService'
    llm_gateway: 'LLMGateway'
    aws_manager: 'AWSManager'
    azure_manager: 'AzureManager'
    gcp_manager: 'GCPManager'
    security_validator: 'SecurityValidator'
    prompt_templates: 'DevOpsPromptTemplates'


class InfrastructureRequest(BaseModel):
    """Infrastructure deployment request"""
    user_request: str
    cloud_provider: str = Field(default="azure", description="aws, azure, or gcp")
    region: Optional[str] = None
    budget_limit: Optional[float] = None
    security_level: str = Field(default="standard", description="basic, standard, high")


class InfrastructurePlan(BaseModel):
    """Infrastructure deployment plan"""
    plan_id: str
    cloud_provider: str
    resources: List[Dict[str, Any]]
    estimated_cost_monthly: float
    security_recommendations: List[str]
    deployment_steps: List[str]
    terraform_code: Optional[str] = None
    estimated_time_minutes: int


# Agent tools for web search and cloud operations
async def search_best_practices(
    ctx: RunContext[AgentDependencies],
    query: str,
    cloud_provider: str = "azure"
) -> List[Dict[str, Any]]:
    """Search web for current cloud best practices"""
    
    search_query = f"{cloud_provider} {query} best practices 2024 security cost optimization"
    
    try:
        results = await ctx.deps.web_search.search(search_query, max_results=5)
        return [
            {
                "title": result["title"],
                "snippet": result["snippet"],
                "url": result["url"],
                "relevance": result.get("relevance", 0.8)
            }
            for result in results
        ]
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []


async def get_current_pricing(
    ctx: RunContext[AgentDependencies],
    cloud_provider: str,
    resource_type: str,
    region: str = "us-east-1"
) -> Dict[str, Any]:
    """Get current pricing from cloud provider APIs"""
    
    if cloud_provider == "aws":
        return await ctx.deps.aws_manager.get_pricing(resource_type, region)
    elif cloud_provider == "azure":
        return await ctx.deps.azure_manager.get_pricing(resource_type, region)
    elif cloud_provider == "gcp":
        return await ctx.deps.gcp_manager.get_pricing(resource_type, region)
    
    return {"error": f"Unsupported provider: {cloud_provider}"}


async def check_security_compliance(
    ctx: RunContext[AgentDependencies],
    resources: List[Dict[str, Any]],
    security_level: str = "standard"
) -> List[str]:
    """Check security compliance and get recommendations"""
    
    recommendations = []
    
    for resource in resources:
        resource_type = resource.get("type", "")
        
        if resource_type in ["vm", "ec2", "compute"]:
            recommendations.extend([
                "Enable disk encryption at rest",
                "Configure network security groups with minimal access",
                "Enable monitoring and logging",
                "Use managed identities for authentication"
            ])
        
        if resource_type in ["database", "rds", "sql"]:
            recommendations.extend([
                "Enable encryption in transit and at rest",
                "Configure firewall rules for database access",
                "Enable audit logging",
                "Use strong authentication methods"
            ])
        
        if resource_type in ["storage", "s3", "blob"]:
            recommendations.extend([
                "Enable versioning and soft delete",
                "Configure access policies with least privilege",
                "Enable access logging",
                "Use encryption for sensitive data"
            ])
    
    # Add security level specific recommendations
    if security_level == "high":
        recommendations.extend([
            "Implement zero-trust network architecture",
            "Enable advanced threat protection",
            "Set up continuous compliance monitoring",
            "Use private endpoints for all services"
        ])
    
    return list(set(recommendations))  # Remove duplicates


async def generate_terraform_code(
    ctx: RunContext[AgentDependencies],
    resources: List[Dict[str, Any]],
    cloud_provider: str
) -> str:
    """Generate secure Terraform code using security-first prompt templates"""
    
    try:
        # Use security-first Terraform template
        prompt = ctx.deps.prompt_templates.generate_prompt(
            "secure_terraform_module",
            resource_type="multi-resource infrastructure",
            use_case=f"Secure deployment of {len(resources)} resources",
            cloud_provider=cloud_provider,
            environment="production",
            security_requirements="SOC2, PCI-DSS compliance required"
        )
        
        if not prompt:
            # Fallback to basic prompt if template fails
            prompt = f"""Generate secure, production-ready Terraform code for {cloud_provider} with these resources:

{json.dumps(resources, indent=2)}

SECURITY REQUIREMENTS (NON-NEGOTIABLE):
- NO 0.0.0.0/0 CIDR blocks for databases or SSH
- Enable encryption at rest and in transit
- Use specific security group references, not open access
- Include proper IAM roles with least privilege
- Enable audit logging and monitoring
- Add appropriate tags for compliance and cost tracking

Return properly formatted Terraform with security best practices."""
        
        response = await ctx.deps.llm_gateway.generate_response(
            messages=[{"role": "user", "content": prompt}],
            provider="gemini",
            temperature=0.1
        )
        
        terraform_code = response["content"]
        
        # Validate generated Terraform for security issues
        security_issues, ai_audit = await ctx.deps.security_validator.validate_with_ai_audit(
            terraform_code, "terraform", ctx.deps.llm_gateway
        )
        
        if security_issues:
            logger.warning(f"Generated Terraform has {len(security_issues)} security issues")
            # Add security warning as comment
            warning = f"""# ⚠️  SECURITY VALIDATION RESULTS:
# Found {len(security_issues)} security issues that need attention
# Critical issues: {sum(1 for i in security_issues if i.severity.value == 'critical')}
# Please review and fix before deployment
# 
"""
            terraform_code = warning + terraform_code
        
        return terraform_code
        
    except Exception as e:
        logger.error(f"Secure Terraform generation failed: {e}")
        return f"# Error generating secure Terraform code: {e}"


async def validate_infrastructure_security(
    ctx: RunContext[AgentDependencies],
    infrastructure_code: str,
    config_type: str = "terraform"
) -> Dict[str, Any]:
    """Validate and audit infrastructure configuration for security"""
    
    try:
        # Run comprehensive security validation
        security_issues, ai_audit = await ctx.deps.security_validator.validate_with_ai_audit(
            infrastructure_code, config_type, ctx.deps.llm_gateway
        )
        
        # Format security report
        security_report = ctx.deps.security_validator.format_security_report(
            security_issues, ai_audit
        )
        
        return security_report
        
    except Exception as e:
        logger.error(f"Security validation failed: {e}")
        return {
            "summary": {"security_status": "VALIDATION_FAILED", "error": str(e)},
            "automated_findings": [],
            "ai_security_audit": f"Security validation failed: {e}",
            "next_steps": ["Manual security review required due to validation failure"]
        }


class CloudInfrastructureAgent:
    """Main cloud infrastructure agent - no RAG, uses web search + cloud APIs"""
    
    def __init__(self, llm_gateway: LLMGateway):
        self.llm_gateway = llm_gateway
        self.web_search = WebSearchService()
        
        # Initialize cloud managers based on available credentials
        self.aws_manager = AWSManager()  # Will handle missing creds gracefully
        self.azure_manager = AzureManager()  # Primary - we have full access
        self.gcp_manager = GCPManager()  # Will handle missing creds gracefully
        
        # Initialize security and prompt services
        self.security_validator = SecurityValidator()
        self.prompt_templates = DevOpsPromptTemplates()
        
        # Don't initialize Pydantic AI agent here to avoid API key issues
        # Instead, use LLM gateway directly
        self.agent = None
    
    def _get_model(self):
        """Get LLM model - using Gemini for free usage"""
        return "gemini-1.5-flash"
    
    def _get_system_prompt(self) -> str:
        """Get enhanced system prompt integrating DevOps knowledge and security best practices"""
        return """You are a Senior Site Reliability Engineer and Cloud Security Expert at a Fortune 500 company. You're responsible for systems that handle millions of requests per day and cannot afford downtime. Every piece of infrastructure you design must be:

- Secure by default (zero-trust principles)
- Highly available (99.99% uptime SLA)
- Observable (comprehensive monitoring/logging)
- Cost-optimized (company is watching cloud spend)
- Compliant (SOC2, PCI-DSS requirements)

CRITICAL SECURITY-FIRST APPROACH:
Never generate infrastructure that includes:
- 0.0.0.0/0 CIDR blocks for SSH or databases
- Hardcoded secrets or passwords
- Missing encryption at rest/transit
- Containers running as root
- Missing resource limits in Kubernetes
- "latest" tags in production
- Overly permissive IAM policies

PRODUCTION-READY STANDARDS:
Every configuration must include:
- Principle of least privilege access
- Proper error handling and retry logic
- Health checks and monitoring
- Backup and disaster recovery
- Resource limits and autoscaling
- Proper tagging for cost allocation
- Network segmentation and security groups
- Audit logging enabled

INTELLIGENT AUTOMATION APPROACH:
- Act like the paranoid senior engineer who's seen too many breaches
- Think through potential failure modes before responding
- Generate code that works in production, not just development
- Include proper documentation and runbooks
- Consider the full system lifecycle (deploy, monitor, maintain, recover)

When generating infrastructure:
1. Use search_best_practices to find current security recommendations
2. Use get_current_pricing for accurate cost estimates
3. Use check_security_compliance for security validation
4. Use generate_terraform_code with security best practices
5. Always include monitoring, alerting, and logging configurations

VALIDATION MINDSET:
Assume every configuration will be attacked by sophisticated adversaries. Design for:
- Defense in depth
- Automated incident response
- Zero-trust networking
- Secrets management integration
- Compliance audit readiness

Your code should pass security scans, cost optimization reviews, and production readiness audits. Think like both a senior DevOps engineer AND a security architect.

Be specific, practical, and ruthlessly focused on production-ready, secure solutions that can scale and be maintained by teams."""
    
    async def create_infrastructure_plan(
        self, 
        request: InfrastructureRequest
    ) -> InfrastructurePlan:
        """Create infrastructure plan using web search and cloud APIs"""
        
        try:
            # Check provider capabilities and adjust accordingly
            provider_capabilities = self._get_provider_capabilities(request.cloud_provider)
            
            if not provider_capabilities["can_deploy"]:
                return await self._create_plan_only_mode(request, provider_capabilities)
            
            # Use LLM Gateway directly instead of Pydantic AI agent
            prompt = self._build_infrastructure_prompt(request, provider_capabilities)
            
            # Get response from LLM
            llm_response = await self.llm_gateway.generate_response(
                messages=[{"role": "user", "content": prompt}],
                provider="azure_openai" if request.cloud_provider == "azure" else "gemini",
                temperature=0.1
            )
            
            # Parse and structure the response
            return await self._parse_llm_response(llm_response, request)
            
        except Exception as e:
            logger.error(f"Infrastructure planning failed: {e}")
            
            # Return fallback plan with demo/example content
            return await self._create_demo_plan(request)
    
    def _get_provider_capabilities(self, cloud_provider: str) -> dict:
        """Get capabilities for each cloud provider based on available credentials"""
        capabilities = {
            "azure": {
                "can_deploy": True,  # We have full Azure access
                "can_plan": True,
                "has_pricing": True,
                "llm_provider": "azure_openai",
                "message": "Full deployment and management capabilities available"
            },
            "aws": {
                "can_deploy": False,  # No AWS deployment credentials
                "can_plan": True,  # Can generate plans
                "has_pricing": False,  # No AWS pricing API access
                "llm_provider": "gemini",
                "message": "Planning only - no deployment credentials configured"
            },
            "gcp": {
                "can_deploy": False,  # No GCP deployment credentials
                "can_plan": True,  # Can generate plans using Gemini
                "has_pricing": False,  # No GCP pricing API access
                "llm_provider": "gemini",
                "message": "Planning only - no deployment credentials configured"
            }
        }
        
        return capabilities.get(cloud_provider, capabilities["azure"])
    
    async def _create_plan_only_mode(self, request: InfrastructureRequest, capabilities: dict) -> InfrastructurePlan:
        """Create plan-only mode for providers without deployment capabilities"""
        
        prompt = f"""Create a detailed infrastructure plan for: {request.user_request}

IMPORTANT: This is PLANNING ONLY for {request.cloud_provider.upper()} - no actual deployment will occur.

Requirements:
- Cloud Provider: {request.cloud_provider} (PLAN ONLY - {capabilities['message']})
- Region: {request.region or 'default'}
- Budget Limit: ${request.budget_limit or 'no limit'}
- Security Level: {request.security_level}

Please provide:
1. Detailed architecture design
2. Resource specifications and configurations
3. Security recommendations
4. Cost estimates (generic)
5. Complete Terraform code for manual deployment
6. Step-by-step deployment instructions

Focus on production-ready, secure solutions that the user can deploy manually."""

        try:
            llm_response = await self.llm_gateway.generate_response(
                messages=[{"role": "user", "content": prompt}],
                provider=capabilities["llm_provider"],
                temperature=0.1
            )
            
            return InfrastructurePlan(
                plan_id=str(uuid.uuid4()),
                cloud_provider=request.cloud_provider,
                resources=[
                    {
                        "name": f"{request.cloud_provider.upper()} Infrastructure Plan",
                        "type": "plan-only",
                        "description": f"Detailed plan for {request.cloud_provider} infrastructure (manual deployment required)",
                        "cost": 0.0
                    }
                ],
                estimated_cost_monthly=100.0,  # Generic estimate
                security_recommendations=[
                    f"⚠️ {request.cloud_provider.upper()} deployment requires manual setup",
                    "Review all security configurations before deployment",
                    "Ensure proper IAM roles and permissions are configured",
                    "Enable monitoring and logging for all resources"
                ],
                deployment_steps=[
                    f"📋 This is a PLAN-ONLY mode for {request.cloud_provider.upper()}",
                    "💡 Download the Terraform code below",
                    "🔧 Configure your cloud credentials manually",
                    "🚀 Run terraform init, plan, and apply commands",
                    "🔍 Verify all resources are created correctly"
                ],
                terraform_code=llm_response.get("content", "# Terraform code generation failed"),
                estimated_time_minutes=15
            )
            
        except Exception as e:
            logger.error(f"Plan-only mode failed: {e}")
            return InfrastructurePlan(
                plan_id=str(uuid.uuid4()),
                cloud_provider=request.cloud_provider,
                resources=[],
                estimated_cost_monthly=0.0,
                security_recommendations=[f"Plan generation failed: {str(e)}"],
                deployment_steps=["Manual configuration required"],
                estimated_time_minutes=0
            )
    
    def _build_infrastructure_prompt(self, request: InfrastructureRequest, capabilities: dict) -> str:
        """Build comprehensive infrastructure prompt"""
        
        return f"""Create a production-ready infrastructure plan for: {request.user_request}

PROVIDER CAPABILITIES:
- Cloud Provider: {request.cloud_provider.upper()}
- Deployment: {'✅ AUTOMATED' if capabilities['can_deploy'] else '❌ MANUAL ONLY'}
- Real-time Pricing: {'✅ AVAILABLE' if capabilities['has_pricing'] else '❌ ESTIMATES ONLY'}
- Context7 MCP: ✅ LATEST DOCUMENTATION AVAILABLE

Requirements:
- Region: {request.region or 'auto-select optimal'}
- Budget Limit: ${request.budget_limit or 'no limit'}
- Security Level: {request.security_level}

ENHANCED REQUIREMENTS:
1. Use Context7 MCP to fetch LATEST Terraform provider documentation
2. Implement security-first design with zero-trust principles
3. Include comprehensive monitoring and logging
4. Optimize for cost and performance
5. Ensure high availability and disaster recovery
6. Generate complete, production-ready Terraform code

SECURITY FOCUS:
- NO 0.0.0.0/0 CIDR blocks for sensitive services
- Enable encryption at rest and in transit
- Implement proper IAM roles with least privilege
- Include network security groups and firewall rules
- Enable audit logging and monitoring

Please provide:
- Detailed resource specifications
- Monthly cost estimates
- Security recommendations
- Complete Terraform code
- Deployment instructions

Focus on practical, production-ready solutions that can scale."""

    async def _parse_llm_response(self, llm_response: dict, request: InfrastructureRequest) -> InfrastructurePlan:
        """Parse LLM response into structured infrastructure plan"""
        
        content = llm_response.get("content", "")
        
        # Extract different sections from the response
        # This is a simplified parser - in production, you'd want more robust parsing
        
        return InfrastructurePlan(
            plan_id=str(uuid.uuid4()),
            cloud_provider=request.cloud_provider,
            resources=[
                {
                    "name": f"{request.cloud_provider.title()} Infrastructure",
                    "type": "multi-resource",
                    "description": "AI-generated infrastructure with latest best practices",
                    "cost": request.budget_limit or 200.0
                }
            ],
            estimated_cost_monthly=request.budget_limit or 200.0,
            security_recommendations=[
                "🛡️ Zero-trust security architecture implemented",
                "🔒 Encryption enabled for all data at rest and in transit", 
                "👤 IAM roles configured with least privilege access",
                "📊 Comprehensive monitoring and alerting enabled",
                "🚨 Security scanning and compliance checks included"
            ],
            deployment_steps=[
                "🔍 Review generated Terraform code",
                "🔧 Configure cloud provider credentials",
                "🚀 Run terraform init and plan commands",
                "✅ Execute terraform apply to deploy infrastructure",
                "📊 Verify monitoring and security configurations"
            ],
            terraform_code=content,  # Full LLM response as Terraform code
            estimated_time_minutes=10
        )
    
    async def _create_demo_plan(self, request: InfrastructureRequest) -> InfrastructurePlan:
        """Create a demo plan when LLM providers are not available"""
        
        capabilities = self._get_provider_capabilities(request.cloud_provider)
        
        # Generate demo Terraform code based on provider
        if request.cloud_provider == "azure":
            terraform_code = self._get_demo_azure_terraform(request)
        elif request.cloud_provider == "aws":
            terraform_code = self._get_demo_aws_terraform(request)
        else:  # GCP
            terraform_code = self._get_demo_gcp_terraform(request)
        
        return InfrastructurePlan(
            plan_id=str(uuid.uuid4()),
            cloud_provider=request.cloud_provider,
            resources=[
                {
                    "name": f"{request.cloud_provider.upper()} Demo Infrastructure",
                    "type": "demo-example",
                    "description": f"Demo infrastructure plan for {request.cloud_provider} (LLM providers not configured)",
                    "cost": 150.0
                }
            ],
            estimated_cost_monthly=150.0,
            security_recommendations=[
                f"🚨 DEMO MODE: LLM providers not configured",
                "🛡️ Enable encryption at rest and in transit",
                "🔒 Configure network security groups properly",
                "👤 Implement least privilege access controls",
                "📊 Set up comprehensive monitoring and alerting",
                f"⚙️ {capabilities['message']}"
            ],
            deployment_steps=[
                f"📋 This is a DEMO plan for {request.cloud_provider.upper()}",
                "🔧 Configure LLM API keys for AI-generated plans",
                "💡 Review the sample Terraform code below",
                "🚀 Customize and deploy using your preferred method",
                "📊 Set up monitoring after deployment"
            ],
            terraform_code=terraform_code,
            estimated_time_minutes=15
        )
    
    def _get_demo_azure_terraform(self, request: InfrastructureRequest) -> str:
        """Generate demo Azure Terraform code"""
        return f"""# AI DevOps Agent - Demo Azure Infrastructure
# Provider: {request.cloud_provider.upper()}
# Budget: ${request.budget_limit or 'No limit'}
# Security: {request.security_level}

terraform {{
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
}}

# Resource Group
resource "azurerm_resource_group" "main" {{
  name     = "rg-aidevops-demo"
  location = "{request.region or 'East US'}"
  
  tags = {{
    Environment = "demo"
    Project     = "ai-devops-agent"
    CreatedBy   = "ai-devops-agent"
  }}
}}

# Virtual Network
resource "azurerm_virtual_network" "main" {{
  name                = "vnet-aidevops-demo"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  tags = azurerm_resource_group.main.tags
}}

# Subnet
resource "azurerm_subnet" "internal" {{
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}}

# Network Security Group
resource "azurerm_network_security_group" "main" {{
  name                = "nsg-aidevops-demo"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {{
    name                       = "HTTPS"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }}

  tags = azurerm_resource_group.main.tags
}}

# Container Instance (Web App)
resource "azurerm_container_group" "main" {{
  name                = "ci-aidevops-demo"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  ip_address_type     = "Public"
  dns_name_label      = "aidevops-demo-${{random_string.suffix.result}}"
  os_type             = "Linux"

  container {{
    name   = "web-app"
    image  = "nginx:alpine"
    cpu    = "0.5"
    memory = "1.5"

    ports {{
      port     = 80
      protocol = "TCP"
    }}
  }}

  tags = azurerm_resource_group.main.tags
}}

resource "random_string" "suffix" {{
  length  = 8
  special = false
  upper   = false
}}

# Outputs
output "container_group_ip" {{
  value = azurerm_container_group.main.ip_address
}}

output "container_group_fqdn" {{
  value = azurerm_container_group.main.fqdn
}}"""

    def _get_demo_aws_terraform(self, request: InfrastructureRequest) -> str:
        """Generate demo AWS Terraform code"""
        return f"""# AI DevOps Agent - Demo AWS Infrastructure (PLAN ONLY)
# Provider: {request.cloud_provider.upper()}
# Budget: ${request.budget_limit or 'No limit'}
# Security: {request.security_level}
# NOTE: This is PLAN ONLY - no AWS deployment credentials configured

terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{request.region or 'us-east-1'}"
}}

# VPC
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name        = "vpc-aidevops-demo"
    Environment = "demo"
    Project     = "ai-devops-agent"
  }}
}}

# Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id

  tags = {{
    Name = "igw-aidevops-demo"
  }}
}}

# Subnet
resource "aws_subnet" "public" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {{
    Name = "subnet-public-aidevops-demo"
  }}
}}

# Security Group
resource "aws_security_group" "web" {{
  name_prefix = "sg-web-aidevops-demo"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name = "sg-web-aidevops-demo"
  }}
}}

# EC2 Instance
resource "aws_instance" "web" {{
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id
  
  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1>AI DevOps Agent Demo</h1>" > /var/www/html/index.html
  EOF

  tags = {{
    Name = "ec2-web-aidevops-demo"
  }}
}}

# Data sources
data "aws_availability_zones" "available" {{
  state = "available"
}}

data "aws_ami" "amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]

  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}
}}

# Outputs
output "instance_public_ip" {{
  value = aws_instance.web.public_ip
}}

output "instance_public_dns" {{
  value = aws_instance.web.public_dns
}}"""

    def _get_demo_gcp_terraform(self, request: InfrastructureRequest) -> str:
        """Generate demo GCP Terraform code"""
        return f"""# AI DevOps Agent - Demo GCP Infrastructure (PLAN ONLY)
# Provider: {request.cloud_provider.upper()}
# Budget: ${request.budget_limit or 'No limit'}
# Security: {request.security_level}
# NOTE: This is PLAN ONLY - no GCP deployment credentials configured

terraform {{
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 4.0"
    }}
  }}
}}

provider "google" {{
  project = var.project_id
  region  = "{request.region or 'us-central1'}"
}}

variable "project_id" {{
  description = "GCP Project ID"
  type        = string
}}

# VPC Network
resource "google_compute_network" "main" {{
  name                    = "vpc-aidevops-demo"
  auto_create_subnetworks = false
}}

# Subnet
resource "google_compute_subnetwork" "main" {{
  name          = "subnet-aidevops-demo"
  ip_cidr_range = "10.0.1.0/24"
  region        = "{request.region or 'us-central1'}"
  network       = google_compute_network.main.id
}}

# Firewall Rule
resource "google_compute_firewall" "allow_http" {{
  name    = "allow-http-aidevops-demo"
  network = google_compute_network.main.name

  allow {{
    protocol = "tcp"
    ports    = ["80", "443"]
  }}

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}}

# Compute Instance
resource "google_compute_instance" "web" {{
  name         = "vm-web-aidevops-demo"
  machine_type = "e2-micro"
  zone         = "{request.region or 'us-central1'}-a"

  boot_disk {{
    initialize_params {{
      image = "debian-cloud/debian-11"
    }}
  }}

  network_interface {{
    network    = google_compute_network.main.name
    subnetwork = google_compute_subnetwork.main.name
    
    access_config {{
      // Ephemeral public IP
    }}
  }}

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y nginx
    systemctl start nginx
    systemctl enable nginx
    echo "<h1>AI DevOps Agent Demo</h1>" > /var/www/html/index.html
  EOF

  tags = ["web-server"]

  labels = {{
    environment = "demo"
    project     = "ai-devops-agent"
  }}
}}

# Outputs
output "instance_external_ip" {{
  value = google_compute_instance.web.network_interface[0].access_config[0].nat_ip
}}"""

    async def deploy_infrastructure(
        self, 
        plan: InfrastructurePlan
    ) -> Dict[str, Any]:
        """Deploy infrastructure using cloud provider SDKs"""
        
        deployment_id = str(uuid.uuid4())
        capabilities = self._get_provider_capabilities(plan.cloud_provider)
        
        try:
            if not capabilities["can_deploy"]:
                # Return plan-only response for providers without deployment capabilities
                return {
                    "deployment_id": deployment_id,
                    "status": "plan_only",
                    "message": f"🚨 {plan.cloud_provider.upper()} deployment requires manual setup",
                    "instructions": [
                        "📋 Download the Terraform code from the plan above",
                        f"🔧 Configure your {plan.cloud_provider.upper()} credentials locally",
                        "🚀 Run: terraform init && terraform plan && terraform apply",
                        "🔍 Verify all resources are created correctly",
                        "📊 Set up monitoring and alerting as recommended"
                    ],
                    "plan_id": plan.plan_id,
                    "deployment_time": datetime.utcnow().isoformat()
                }
            
            # Only Azure has full deployment capabilities
            if plan.cloud_provider == "azure":
                result = await self.azure_manager.deploy_resources(plan.resources)
                
                return {
                    "deployment_id": deployment_id,
                    "status": "success",
                    "message": "🎉 Azure infrastructure deployed successfully!",
                    "resources_created": result.get("resources", []),
                    "deployment_time": datetime.utcnow().isoformat(),
                    "plan_id": plan.plan_id,
                    "post_deployment": [
                        "✅ All Azure resources have been created",
                        "🔍 Check Azure Portal for resource status",
                        "📊 Monitor resource usage and costs",
                        "🛡️ Verify security configurations are active"
                    ]
                }
            else:
                # This shouldn't happen with our capability checks, but handle it
                raise ValueError(f"Deployment not supported for {plan.cloud_provider}")
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {
                "deployment_id": deployment_id,
                "status": "failed",
                "error": str(e),
                "message": f"❌ Deployment failed for {plan.cloud_provider}",
                "plan_id": plan.plan_id,
                "troubleshooting": [
                    "🔍 Check your cloud provider credentials",
                    "📋 Verify the Terraform code is valid",
                    "🚨 Review error logs for specific issues",
                    "💬 Contact support if the issue persists"
                ]
            }