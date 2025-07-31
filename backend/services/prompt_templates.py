#!/usr/bin/env python3
"""
DevOps Prompt Templates
Inspired by 50_ai_prompts.txt for intelligent automation
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class PromptCategory(Enum):
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    KUBERNETES = "kubernetes"
    CICD = "cicd"
    MONITORING = "monitoring"
    TROUBLESHOOTING = "troubleshooting"


@dataclass
class PromptTemplate:
    name: str
    category: PromptCategory
    description: str
    template: str
    required_params: List[str]
    optional_params: List[str] = None
    example_usage: str = ""


class DevOpsPromptTemplates:
    """
    Intelligent prompt templates based on 50 AI prompts for DevOps automation
    Each template is crafted for production-ready, secure infrastructure
    """
    
    def __init__(self):
        self.templates = self._init_templates()
    
    def _init_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize all prompt templates from 50 AI prompts wisdom"""
        
        templates = {}
        
        # Security-First Infrastructure Templates
        templates["secure_terraform_module"] = PromptTemplate(
            name="Secure Terraform Module",
            category=PromptCategory.INFRASTRUCTURE,
            description="Generate production-ready Terraform with security best practices",
            template="""Act as a Senior Cloud Security Engineer. Generate {resource_type} for {use_case} following these non-negotiable requirements:

Security:
- Implement principle of least privilege
- Enable encryption at rest and in transit
- Use security groups/NACLs with minimal required access
- Include WAF rules if web-facing
- Enable detailed logging and monitoring
- NO 0.0.0.0/0 CIDR blocks for sensitive services
- NO hardcoded secrets or passwords

Reliability:
- Include health checks and auto-scaling
- Implement proper retry logic and circuit breakers
- Plan for multi-AZ/region deployment
- Set appropriate resource limits and requests

Compliance:
- Add required tags for cost allocation and compliance
- Include data classification labels
- Ensure GDPR/SOC2 compliance where applicable
- Enable audit logging

Operations:
- Include monitoring and alerting configurations
- Plan deployment and rollback strategies
- Document environment-specific configurations
- Include cost optimization recommendations

Cloud Provider: {cloud_provider}
Environment: {environment}
Security Requirements: {security_requirements}

Generate production-ready configuration that would pass security audit.""",
            required_params=["resource_type", "use_case", "cloud_provider"],
            optional_params=["environment", "security_requirements"],
            example_usage="Create secure S3 bucket with versioning for document storage"
        )
        
        templates["kubernetes_security_manifest"] = PromptTemplate(
            name="Production Kubernetes Manifest",
            category=PromptCategory.KUBERNETES,
            description="Generate secure, production-ready Kubernetes manifests",
            template="""Create production-ready Kubernetes manifests for {application_name} following security best practices:

Security Requirements:
- Containers must run as non-root user (runAsUser: 10001)
- No privilege escalation allowed
- Read-only root filesystem
- Drop all capabilities
- Use specific image tags (NO 'latest')
- Secrets via volumes, not environment variables
- Resource limits to prevent DoS

Production Standards:
- Horizontal Pod Autoscaler configured
- Pod Disruption Budget for availability
- Liveness and readiness probes
- Init containers if needed
- Persistent volumes for data
- Network policies for segmentation
- Service accounts with minimal permissions

Monitoring & Observability:
- Prometheus metrics endpoints
- Structured logging
- Health check endpoints
- Performance monitoring

Application Details:
- Image: {container_image}
- Ports: {ports}
- Environment: {environment}
- Replicas: {replica_count}
- Resource Requirements: {resource_requirements}

Include deployment, service, configmap, secrets, ingress, and monitoring configurations.""",
            required_params=["application_name", "container_image", "ports"],
            optional_params=["environment", "replica_count", "resource_requirements"],
            example_usage="Deploy payment processing service with high security"
        )
        
        templates["cicd_security_pipeline"] = PromptTemplate(
            name="Secure CI/CD Pipeline",
            category=PromptCategory.CICD,
            description="Generate CI/CD pipeline with security scanning and best practices",
            template="""Create a production-ready CI/CD pipeline for {application_type} with comprehensive security:

Security Scanning (Required):
- SAST (Static Application Security Testing)
- Container image vulnerability scanning
- Infrastructure as Code security scanning
- Secret detection in code
- License compliance checking
- Dependency vulnerability scanning

Pipeline Requirements:
- Multi-environment support: {environments}
- Deploy to: {deployment_target}
- Testing strategy: {testing_requirements}
- Approval workflows for production
- Automated rollback on failure
- Proper secret management (no hardcoded secrets)

Security Gates:
- Block deployment if critical vulnerabilities found
- Require security team approval for production
- Audit trail for all deployments
- Integration with security tools: {security_tools}

Deployment Strategy:
- Blue/green or canary deployment
- Health checks and monitoring
- Automated smoke tests
- Notification to stakeholders

Platform: {platform}
Repository: {repository_type}

Generate complete pipeline configuration with security as the primary focus.""",
            required_params=["application_type", "deployment_target", "platform"],
            optional_params=["environments", "testing_requirements", "security_tools", "repository_type"],
            example_usage="Create secure pipeline for microservices deployment to Kubernetes"
        )
        
        templates["security_audit_prompt"] = PromptTemplate(
            name="AI Security Audit",
            category=PromptCategory.SECURITY,
            description="Generate comprehensive security audit prompts for infrastructure",
            template="""You are a Senior Security Engineer conducting a security audit of the {config_type} you just generated. Your job is to find every possible security vulnerability, compliance issue, and operational risk.

Assume the worst-case scenario: this application handles {data_sensitivity} data, runs in a {environment_type} environment, and will be targeted by sophisticated attackers.

Review the configuration and provide:
1. A severity rating (Critical/High/Medium/Low) for each issue found
2. The specific line or configuration causing the problem
3. The exact fix needed
4. Why this matters in a production environment

Security Focus Areas:
- Authentication and authorization flaws
- Network security and segmentation gaps
- Data encryption missing (at rest and in transit)
- Secret management issues
- Privilege escalation opportunities
- Resource limits missing (DoS prevention)
- Audit logging gaps
- Compliance violations ({compliance_requirements})

Attack Scenarios to Consider:
- Container breakout attempts
- Lateral movement within network
- Data exfiltration possibilities
- Denial of service attacks
- Privilege escalation
- Supply chain attacks

Be paranoid. Be thorough. Pretend you're the one who gets fired if this gets hacked.

For each issue found, provide:
- **SEVERITY**: [Critical/High/Medium/Low]
- **Issue**: [Brief description]
- **Location**: [Specific line or section]
- **Impact**: [What could go wrong]
- **Fix**: [Exact remediation steps]
- **Prevention**: [How to avoid in future]

Also provide:
- Overall security score (1-10)
- Prioritized remediation plan
- Compliance impact assessment""",
            required_params=["config_type"],
            optional_params=["data_sensitivity", "environment_type", "compliance_requirements"],
            example_usage="Audit Terraform configuration for payment processing system"
        )
        
        templates["troubleshooting_guide"] = PromptTemplate(
            name="Production Troubleshooting Runbook",
            category=PromptCategory.TROUBLESHOOTING,
            description="Generate comprehensive troubleshooting guide for production issues",
            template="""Create a troubleshooting runbook for {service_name} covering these failure scenarios:

Common Issues: {common_issues}
Environment: {environment_details}
Architecture: {architecture_overview}

For each failure scenario, provide:

**Immediate Response (First 5 minutes):**
- Symptoms to look for
- Quick health checks to run
- Emergency mitigation steps
- Who to notify immediately

**Investigation Steps (Next 15 minutes):**
- Diagnostic commands to run
- Log locations and what to grep for
- Metrics and dashboards to check
- External dependencies to verify

**Resolution Procedures:**
- Step-by-step fix instructions
- Rollback procedures if needed
- Verification steps
- Post-incident cleanup

**Communication:**
- Status page updates
- Stakeholder notifications
- Customer communication templates
- Escalation procedures

**Prevention:**
- Monitoring improvements
- Alerting enhancements
- Process improvements
- Training recommendations

Make this usable by junior engineers during high-stress situations. Include:
- Required access and permissions
- Command examples with expected output
- Decision trees for different scenarios
- Contact information and escalation paths

Focus on {priority_areas} as the most critical areas.""",
            required_params=["service_name", "common_issues"],
            optional_params=["environment_details", "architecture_overview", "priority_areas"],
            example_usage="Create runbook for payment API service outages"
        )
        
        templates["monitoring_setup"] = PromptTemplate(
            name="Production Monitoring Configuration",
            category=PromptCategory.MONITORING,
            description="Generate comprehensive monitoring and alerting setup",
            template="""Design comprehensive monitoring and alerting for {service_name} with these requirements:

Service Details:
- Architecture: {architecture_type}
- Critical SLAs: {sla_requirements}
- User Impact: {user_impact_scenarios}
- Team Size: {team_size} engineers

Monitoring Strategy:
1. **Application Metrics**
   - Business metrics: {business_metrics}
   - Performance metrics: {performance_metrics}
   - Error rates and types
   - User experience metrics

2. **Infrastructure Metrics**
   - Resource utilization (CPU, memory, disk, network)
   - Container/pod health and restarts
   - Database performance and connections
   - Network latency and throughput

3. **Security Metrics**
   - Failed authentication attempts
   - Unusual traffic patterns
   - Permission escalation attempts
   - Data access patterns

Alerting Requirements:
- Minimize false positives
- Catch real issues before users notice
- Provide actionable information
- Include runbook links
- Proper escalation chains

Alert Severity Levels:
- **Critical**: Immediate response required (page on-call)
- **High**: Response within 1 hour
- **Medium**: Response within 4 hours
- **Low**: Review during business hours

Dashboard Requirements:
- Executive summary (health overview)
- Operations dashboard (detailed metrics)
- Troubleshooting views
- Capacity planning metrics

Tools Available: {monitoring_tools}
Current Pain Points: {current_issues}

Generate complete monitoring configuration including:
- Metric collection setup
- Alert definitions with thresholds
- Dashboard configurations
- Notification routing
- SLO/SLI definitions""",
            required_params=["service_name", "sla_requirements"],
            optional_params=["architecture_type", "user_impact_scenarios", "team_size", "business_metrics", "performance_metrics", "monitoring_tools", "current_issues"],
            example_usage="Set up monitoring for microservices e-commerce platform"
        )
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get specific template by name"""
        return self.templates.get(template_name)
    
    def get_templates_by_category(self, category: PromptCategory) -> List[PromptTemplate]:
        """Get all templates in a specific category"""
        return [template for template in self.templates.values() 
                if template.category == category]
    
    def generate_prompt(
        self, 
        template_name: str, 
        **params
    ) -> Optional[str]:
        """Generate a prompt from template with provided parameters"""
        template = self.get_template(template_name)
        if not template:
            logger.error(f"Template '{template_name}' not found")
            return None
        
        # Check required parameters
        missing_params = [param for param in template.required_params 
                         if param not in params]
        if missing_params:
            logger.error(f"Missing required parameters: {missing_params}")
            return None
        
        try:
            # Generate prompt with parameters
            prompt = template.template.format(**params)
            return prompt
        except KeyError as e:
            logger.error(f"Parameter formatting error: {e}")
            return None
    
    def list_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """List all available templates with their metadata"""
        return {
            name: {
                "category": template.category.value,
                "description": template.description,
                "required_params": template.required_params,
                "optional_params": template.optional_params or [],
                "example_usage": template.example_usage
            }
            for name, template in self.templates.items()
        }
    
    def get_security_first_recommendations(self) -> List[str]:
        """Get security-first recommendations based on knowledge documents"""
        return [
            "🔒 Always start with security requirements, not features",
            "🚫 Never use 0.0.0.0/0 CIDR blocks for databases or SSH",
            "🔑 Use managed secret services, never hardcode credentials", 
            "🛡️  Implement principle of least privilege for all access",
            "📊 Enable comprehensive audit logging for compliance",
            "🔄 Use specific version tags, never 'latest' in production",
            "⚡ Set resource limits to prevent DoS attacks",
            "🔍 Implement defense in depth with multiple security layers",
            "📋 Assume every configuration will be attacked by experts",
            "🎯 Design for zero-trust networking from the start"
        ]