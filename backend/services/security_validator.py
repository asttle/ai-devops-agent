#!/usr/bin/env python3
"""
Security Validation Service
Inspired by AI DevOps Knowledge and 50 AI Prompts best practices
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class SecuritySeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SecurityIssue:
    severity: SecuritySeverity
    issue_type: str
    description: str
    line_reference: Optional[str]
    fix_recommendation: str
    rationale: str


class SecurityValidator:
    """
    AI-powered security validator based on real-world DevOps failures
    Implements the security checks from ai_devops_knowledge.txt
    """
    
    def __init__(self):
        self.security_patterns = self._init_security_patterns()
    
    def _init_security_patterns(self) -> Dict[str, Dict]:
        """Initialize security validation patterns from DevOps knowledge"""
        return {
            "terraform": {
                "critical_patterns": [
                    {
                        "pattern": r'cidr_blocks\s*=\s*\["0\.0\.0\.0/0"\]',
                        "description": "Overly permissive CIDR block (0.0.0.0/0)",
                        "fix": "Use specific IP ranges or security group references",
                        "rationale": "Exposes resources to entire internet - major attack vector"
                    },
                    {
                        "pattern": r'password\s*=\s*["\'][^"\']*["\']',
                        "description": "Hardcoded password in configuration",
                        "fix": "Use AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager",
                        "rationale": "Secrets in code can be exposed in version control"
                    },
                    {
                        "pattern": r'storage_encrypted\s*=\s*false',
                        "description": "Storage encryption disabled",
                        "fix": "Enable encryption: storage_encrypted = true",
                        "rationale": "Unencrypted data at rest violates compliance requirements"
                    }
                ],
                "high_patterns": [
                    {
                        "pattern": r'from_port\s*=\s*22.*to_port\s*=\s*22.*0\.0\.0\.0/0',
                        "description": "SSH access open to internet",
                        "fix": "Use Systems Manager Session Manager or bastion hosts",
                        "rationale": "Direct SSH access is a common attack vector"
                    },
                    {
                        "pattern": r'skip_final_snapshot\s*=\s*true',
                        "description": "Database final snapshot disabled",
                        "fix": "Enable final snapshots for production databases",
                        "rationale": "Data loss prevention for database deletions"
                    }
                ]
            },
            "kubernetes": {
                "critical_patterns": [
                    {
                        "pattern": r'runAsUser:\s*0',
                        "description": "Container running as root user",
                        "fix": "Set runAsUser to non-root (e.g., 10001)",
                        "rationale": "Root containers have full host privileges if escaped"
                    },
                    {
                        "pattern": r'image:.*:latest',
                        "description": "Using 'latest' image tag",
                        "fix": "Use specific version tags (e.g., v1.2.3)",
                        "rationale": "Latest tags prevent deployment reproducibility"
                    },
                    {
                        "pattern": r'value:\s*["\'].*(?:password|secret|key).*["\']',
                        "description": "Secrets in environment variables",
                        "fix": "Use Kubernetes secrets with secret volumes",
                        "rationale": "Environment variables can be exposed in process lists"
                    }
                ],
                "high_patterns": [
                    {
                        "pattern": r'kind:\s*Deployment(?:(?!resources:).)*$',
                        "description": "Missing resource limits in deployment",
                        "fix": "Add CPU and memory requests/limits",
                        "rationale": "Prevents resource exhaustion and cluster instability"
                    },
                    {
                        "pattern": r'allowPrivilegeEscalation:\s*true',
                        "description": "Privilege escalation allowed",
                        "fix": "Set allowPrivilegeEscalation: false",
                        "rationale": "Prevents container breakout attacks"
                    }
                ]
            },
            "docker": {
                "critical_patterns": [
                    {
                        "pattern": r'USER\s+root',
                        "description": "Dockerfile using root user",
                        "fix": "Create and use non-root user",
                        "rationale": "Root users increase container security risks"
                    },
                    {
                        "pattern": r'COPY\s+.*\s+/',
                        "description": "Copying files to root filesystem",
                        "fix": "Copy to specific application directories",
                        "rationale": "Avoids overwriting system files"
                    }
                ]
            }
        }
    
    async def validate_infrastructure_config(
        self, 
        config_content: str, 
        config_type: str = "terraform"
    ) -> List[SecurityIssue]:
        """
        Validate infrastructure configuration for security issues
        Based on real-world failures from ai_devops_knowledge.txt
        """
        issues = []
        
        if config_type not in self.security_patterns:
            logger.warning(f"Unknown configuration type: {config_type}")
            return issues
        
        patterns = self.security_patterns[config_type]
        
        # Check critical patterns
        for pattern_config in patterns.get("critical_patterns", []):
            matches = re.finditer(pattern_config["pattern"], config_content, re.MULTILINE | re.DOTALL)
            for match in matches:
                line_num = config_content[:match.start()].count('\n') + 1
                
                issues.append(SecurityIssue(
                    severity=SecuritySeverity.CRITICAL,
                    issue_type="security_vulnerability",
                    description=pattern_config["description"],
                    line_reference=f"Line {line_num}",
                    fix_recommendation=pattern_config["fix"],
                    rationale=pattern_config["rationale"]
                ))
        
        # Check high severity patterns
        for pattern_config in patterns.get("high_patterns", []):
            matches = re.finditer(pattern_config["pattern"], config_content, re.MULTILINE | re.DOTALL)
            for match in matches:
                line_num = config_content[:match.start()].count('\n') + 1
                
                issues.append(SecurityIssue(
                    severity=SecuritySeverity.HIGH,
                    issue_type="security_risk",
                    description=pattern_config["description"],
                    line_reference=f"Line {line_num}",
                    fix_recommendation=pattern_config["fix"],
                    rationale=pattern_config["rationale"]
                ))
        
        return issues
    
    async def generate_security_audit_prompt(self, config_content: str, config_type: str) -> str:
        """
        Generate AI audit prompt based on 50_ai_prompts.txt wisdom
        This creates the "AI auditing AI" approach from the knowledge document
        """
        
        audit_prompt = f"""You are a Senior Security Engineer conducting a security audit of the {config_type} configuration below. Your job is to find every possible security vulnerability, compliance issue, and operational risk.

Assume the worst-case scenario: this application handles PCI-compliant payment data, runs in a shared environment with other workloads, and will be targeted by sophisticated attackers.

Configuration to audit:
```{config_type}
{config_content}
```

Review this configuration and provide:
1. A severity rating (Critical/High/Medium/Low) for each issue found
2. The specific line or configuration causing the problem
3. The exact fix needed
4. Why this matters in a production environment

Focus on these critical security areas:
- Authentication and authorization
- Network security and segmentation
- Data encryption (at rest and in transit)
- Secret management
- Privilege escalation prevention
- Resource limits and DoS prevention
- Audit logging and monitoring
- Compliance requirements (SOC2, PCI-DSS)

Be paranoid. Be thorough. Pretend you're the one who gets fired if this gets hacked.

For each issue, use this format:
**SEVERITY: [Critical/High/Medium/Low]**
- Issue: [Brief description]
- Location: [Specific line or section]
- Impact: [What could go wrong]
- Fix: [Exact remediation steps]
- Prevention: [How to avoid in future]

Also provide an overall security score (1-10) and prioritized remediation plan."""

        return audit_prompt
    
    async def validate_with_ai_audit(
        self, 
        config_content: str, 
        config_type: str, 
        llm_gateway
    ) -> Tuple[List[SecurityIssue], str]:
        """
        Use AI to audit configuration and return both automated and AI-generated findings
        Implements the "AI auditing AI" pattern from the knowledge documents
        """
        # Get automated security issues
        automated_issues = await self.validate_infrastructure_config(config_content, config_type)
        
        # Generate AI audit prompt
        audit_prompt = await self.generate_security_audit_prompt(config_content, config_type)
        
        try:
            # Get AI security audit
            ai_response = await llm_gateway.generate_response(
                messages=[{"role": "user", "content": audit_prompt}],
                provider="gemini",  # Use free provider for security audits
                temperature=0.1  # Low temperature for consistent security analysis
            )
            
            ai_audit_result = ai_response.get("content", "AI audit failed")
            
            logger.info(f"AI security audit completed for {config_type} configuration")
            
        except Exception as e:
            logger.error(f"AI security audit failed: {e}")
            ai_audit_result = f"AI security audit failed: {str(e)}"
        
        return automated_issues, ai_audit_result
    
    def format_security_report(
        self, 
        automated_issues: List[SecurityIssue], 
        ai_audit: str
    ) -> Dict[str, Any]:
        """Format comprehensive security report"""
        
        critical_count = sum(1 for issue in automated_issues if issue.severity == SecuritySeverity.CRITICAL)
        high_count = sum(1 for issue in automated_issues if issue.severity == SecuritySeverity.HIGH)
        
        return {
            "summary": {
                "total_issues": len(automated_issues),
                "critical_issues": critical_count,
                "high_issues": high_count,
                "security_status": "FAIL" if critical_count > 0 else "REVIEW" if high_count > 0 else "PASS"
            },
            "automated_findings": [
                {
                    "severity": issue.severity.value,
                    "type": issue.issue_type,
                    "description": issue.description,
                    "location": issue.line_reference,
                    "fix": issue.fix_recommendation,
                    "rationale": issue.rationale
                }
                for issue in automated_issues
            ],
            "ai_security_audit": ai_audit,
            "next_steps": self._generate_next_steps(automated_issues),
            "compliance_notes": self._generate_compliance_notes(automated_issues)
        }
    
    def _generate_next_steps(self, issues: List[SecurityIssue]) -> List[str]:
        """Generate prioritized next steps based on issues found"""
        next_steps = []
        
        critical_issues = [i for i in issues if i.severity == SecuritySeverity.CRITICAL]
        if critical_issues:
            next_steps.append("🚨 IMMEDIATE: Fix all critical security vulnerabilities before deployment")
            
        high_issues = [i for i in issues if i.severity == SecuritySeverity.HIGH]
        if high_issues:
            next_steps.append("⚠️  HIGH PRIORITY: Address high-risk security issues within 24 hours")
            
        next_steps.extend([
            "🔍 Run additional security scans (tfsec, checkov, snyk)",
            "📋 Review with security team before production deployment",
            "🔄 Implement automated security validation in CI/CD pipeline"
        ])
        
        return next_steps
    
    def _generate_compliance_notes(self, issues: List[SecurityIssue]) -> Dict[str, str]:
        """Generate compliance-related notes"""
        return {
            "SOC2": "Address encryption and access control issues for SOC2 compliance",
            "PCI_DSS": "Ensure network segmentation and encryption for payment data",
            "GDPR": "Verify data protection and audit logging requirements",
            "HIPAA": "Confirm encryption and access controls for healthcare data"
        }