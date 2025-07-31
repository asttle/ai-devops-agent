#!/usr/bin/env python3
"""
Context7 MCP integration for accessing latest documentation
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import structlog

logger = structlog.get_logger(__name__)


class Context7MCPClient:
    """Context7 MCP client for accessing latest documentation"""
    
    def __init__(self):
        self.base_url = "https://api.context7.com/v1"  # Hypothetical Context7 API
        self.timeout = 30.0
        self.session: Optional[httpx.AsyncClient] = None
        
        # Documentation sources that Context7 can access
        self.doc_sources = {
            "aws": {
                "base_url": "https://docs.aws.amazon.com",
                "services": ["ec2", "rds", "lambda", "eks", "s3", "cloudformation"],
                "last_updated": None
            },
            "azure": {
                "base_url": "https://docs.microsoft.com/en-us/azure",
                "services": ["vm", "sql", "functions", "aks", "storage", "arm"],
                "last_updated": None
            },
            "gcp": {
                "base_url": "https://cloud.google.com/docs",
                "services": ["compute", "sql", "functions", "gke", "storage", "deployment-manager"],
                "last_updated": None
            },
            "kubernetes": {
                "base_url": "https://kubernetes.io/docs",
                "topics": ["concepts", "tutorials", "reference", "best-practices"],
                "last_updated": None
            },
            "terraform": {
                "base_url": "https://registry.terraform.io/providers",
                "providers": ["aws", "azurerm", "google", "kubernetes"],
                "last_updated": None
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def get_latest_documentation(
        self, 
        provider: str, 
        service: str, 
        topic: str = "getting-started"
    ) -> Dict[str, Any]:
        """Get latest documentation from Context7 MCP"""
        
        try:
            # Since Context7 MCP may not exist yet, we'll simulate it with real doc fetching
            return await self._fetch_real_documentation(provider, service, topic)
            
        except Exception as e:
            logger.error(f"Context7 MCP documentation fetch failed: {e}")
            return await self._get_fallback_documentation(provider, service, topic)
    
    async def _fetch_real_documentation(
        self, 
        provider: str, 
        service: str, 
        topic: str
    ) -> Dict[str, Any]:
        """Fetch real documentation from provider docs"""
        
        if not self.session:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        
        doc_urls = {
            "aws": {
                "ec2": "https://docs.aws.amazon.com/ec2/latest/userguide/concepts.html",
                "rds": "https://docs.aws.amazon.com/rds/latest/userguide/CHAP_GettingStarted.html",
                "lambda": "https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html",
                "eks": "https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html"
            },
            "azure": {
                "vm": "https://docs.microsoft.com/en-us/azure/virtual-machines/",
                "sql": "https://docs.microsoft.com/en-us/azure/azure-sql/",
                "functions": "https://docs.microsoft.com/en-us/azure/azure-functions/",
                "aks": "https://docs.microsoft.com/en-us/azure/aks/"
            },
            "gcp": {
                "compute": "https://cloud.google.com/compute/docs",
                "sql": "https://cloud.google.com/sql/docs",
                "functions": "https://cloud.google.com/functions/docs",
                "gke": "https://cloud.google.com/kubernetes-engine/docs"
            }
        }
        
        url = doc_urls.get(provider, {}).get(service)
        if not url:
            return await self._get_fallback_documentation(provider, service, topic)
        
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            
            # Extract relevant content (simplified)
            content = response.text
            
            # Parse and extract key information
            documentation = await self._parse_documentation_content(content, provider, service)
            
            return {
                "provider": provider,
                "service": service,
                "topic": topic,
                "content": documentation,
                "source_url": url,
                "fetched_at": datetime.utcnow().isoformat(),
                "method": "real_fetch"
            }
            
        except Exception as e:
            logger.warning(f"Failed to fetch real documentation from {url}: {e}")
            return await self._get_fallback_documentation(provider, service, topic)
    
    async def _parse_documentation_content(
        self, 
        content: str, 
        provider: str, 
        service: str
    ) -> Dict[str, Any]:
        """Parse HTML documentation content"""
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else f"{provider.upper()} {service.title()}"
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                # Get text content, preserving some structure
                paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'li'])
                content_text = '\n'.join([p.get_text().strip() for p in paragraphs[:20]])  # Limit to first 20 elements
            else:
                content_text = "Documentation content could not be extracted."
            
            # Extract code examples
            code_blocks = soup.find_all(['code', 'pre'])
            code_examples = [block.get_text().strip() for block in code_blocks[:5]]  # First 5 code blocks
            
            return {
                "title": title_text,
                "overview": content_text[:2000],  # Limit overview length
                "code_examples": code_examples,
                "best_practices": await self._extract_best_practices(content_text),
                "common_patterns": await self._extract_common_patterns(provider, service)
            }
            
        except ImportError:
            logger.warning("BeautifulSoup not available, using simplified parsing")
            return {
                "title": f"{provider.upper()} {service.title()} Documentation",
                "overview": content[:1000] if content else "No content available",
                "code_examples": [],
                "best_practices": [],
                "common_patterns": []
            }
        except Exception as e:
            logger.error(f"Documentation parsing failed: {e}")
            return {
                "title": f"{provider.upper()} {service.title()}",
                "overview": "Documentation parsing failed",
                "code_examples": [],
                "best_practices": [],
                "common_patterns": []
            }
    
    async def _extract_best_practices(self, content: str) -> List[str]:
        """Extract best practices from documentation content"""
        
        best_practices = []
        
        # Look for common best practice keywords
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in [
                'best practice', 'recommendation', 'should', 'must', 
                'security', 'performance', 'cost', 'optimize'
            ]):
                if len(line.strip()) > 20 and len(line.strip()) < 200:
                    best_practices.append(line.strip())
        
        return best_practices[:10]  # Limit to top 10
    
    async def _extract_common_patterns(self, provider: str, service: str) -> List[str]:
        """Extract common patterns for the service"""
        
        patterns = {
            "aws": {
                "ec2": [
                    "Use Auto Scaling Groups for high availability",
                    "Implement proper security groups",
                    "Use spot instances for cost optimization",
                    "Enable detailed monitoring"
                ],
                "rds": [
                    "Enable automated backups",
                    "Use Multi-AZ for production",
                    "Implement read replicas for read-heavy workloads",
                    "Configure parameter groups appropriately"
                ]
            },
            "azure": {
                "vm": [
                    "Use managed disks for better reliability",
                    "Implement Azure Backup",
                    "Use availability sets or zones",
                    "Configure network security groups"
                ],
                "sql": [
                    "Enable Transparent Data Encryption",
                    "Use Azure AD authentication",
                    "Configure firewall rules",
                    "Implement automated backups"
                ]
            },
            "gcp": {
                "compute": [
                    "Use preemptible instances for cost savings",
                    "Implement proper IAM roles",
                    "Use startup scripts for configuration",
                    "Enable OS Login for better security"
                ]
            }
        }
        
        return patterns.get(provider, {}).get(service, [])
    
    async def _get_fallback_documentation(
        self, 
        provider: str, 
        service: str, 
        topic: str
    ) -> Dict[str, Any]:
        """Get fallback documentation when real fetch fails"""
        
        fallback_docs = {
            "aws": {
                "ec2": {
                    "title": "Amazon EC2 - Elastic Compute Cloud",
                    "overview": "Amazon Elastic Compute Cloud (EC2) provides scalable computing capacity in the cloud. Use EC2 to launch virtual servers, configure security and networking, and manage storage.",
                    "best_practices": [
                        "Use appropriate instance types for your workload",
                        "Implement Auto Scaling for high availability",
                        "Use spot instances for cost optimization",
                        "Configure security groups with least privilege",
                        "Enable detailed monitoring and logging"
                    ],
                    "code_examples": [
                        "aws ec2 run-instances --image-id ami-12345678 --count 1 --instance-type t3.micro",
                        "aws ec2 create-security-group --group-name my-sg --description 'My security group'"
                    ]
                }
            },
            "azure": {
                "vm": {
                    "title": "Azure Virtual Machines",
                    "overview": "Azure Virtual Machines provide on-demand, scalable computing resources. Create Linux and Windows virtual machines in seconds and pay only for what you use.",
                    "best_practices": [
                        "Use managed disks for better performance and reliability",
                        "Implement Azure Backup for data protection",
                        "Use availability sets or availability zones",
                        "Configure network security groups properly",
                        "Use Azure Monitor for monitoring and alerting"
                    ],
                    "code_examples": [
                        "az vm create --resource-group myResourceGroup --name myVM --image UbuntuLTS",
                        "az vm start --resource-group myResourceGroup --name myVM"
                    ]
                }
            },
            "gcp": {
                "compute": {
                    "title": "Google Compute Engine",
                    "overview": "Compute Engine delivers configurable virtual machines running in Google's data centers with access to high-performance networking infrastructure and block storage solutions.",
                    "best_practices": [
                        "Use preemptible instances for cost savings",
                        "Implement proper IAM roles and permissions",
                        "Use custom machine types for optimal resource usage",
                        "Enable OS Login for centralized user management",
                        "Use persistent disks for data durability"
                    ],
                    "code_examples": [
                        "gcloud compute instances create my-instance --zone=us-central1-a",
                        "gcloud compute instances start my-instance --zone=us-central1-a"
                    ]
                }
            }
        }
        
        provider_docs = fallback_docs.get(provider, {})
        service_docs = provider_docs.get(service, {
            "title": f"{provider.upper()} {service.title()}",
            "overview": f"Documentation for {provider} {service} service",
            "best_practices": [],
            "code_examples": []
        })
        
        return {
            "provider": provider,
            "service": service,
            "topic": topic,
            "content": service_docs,
            "source_url": f"fallback://{provider}/{service}",
            "fetched_at": datetime.utcnow().isoformat(),
            "method": "fallback"
        }
    
    async def get_current_pricing(
        self, 
        provider: str, 
        service: str, 
        region: str = "us-east-1"
    ) -> Dict[str, Any]:
        """Get current pricing information via Context7 MCP"""
        
        # This would use Context7 MCP to get real-time pricing
        # For now, simulate with realistic pricing data
        
        pricing_data = {
            "aws": {
                "ec2": {
                    "t3.nano": {"on_demand": 0.0052, "spot": 0.0016},
                    "t3.micro": {"on_demand": 0.0104, "spot": 0.0031},
                    "t3.small": {"on_demand": 0.0208, "spot": 0.0062},
                    "t3.medium": {"on_demand": 0.0416, "spot": 0.0125}
                },
                "rds": {
                    "db.t3.micro": {"on_demand": 0.017},
                    "db.t3.small": {"on_demand": 0.034}
                }
            },
            "azure": {
                "vm": {
                    "Standard_B1s": {"pay_as_you_go": 0.0052, "spot": 0.00156},
                    "Standard_B2s": {"pay_as_you_go": 0.0208, "spot": 0.00624}
                }
            },
            "gcp": {
                "compute": {
                    "e2-micro": {"on_demand": 0.0063, "preemptible": 0.0019},
                    "e2-small": {"on_demand": 0.0126, "preemptible": 0.0038}
                }
            }
        }
        
        return {
            "provider": provider,
            "service": service,
            "region": region,
            "pricing": pricing_data.get(provider, {}).get(service, {}),
            "currency": "USD",
            "last_updated": datetime.utcnow().isoformat(),
            "source": "context7_mcp_simulation"
        }
    
    async def get_security_recommendations(
        self, 
        provider: str, 
        services: List[str]
    ) -> Dict[str, Any]:
        """Get security recommendations via Context7 MCP"""
        
        recommendations = []
        
        for service in services:
            doc = await self.get_latest_documentation(provider, service, "security")
            if doc and doc.get("content", {}).get("best_practices"):
                service_recommendations = [
                    rec for rec in doc["content"]["best_practices"] 
                    if any(keyword in rec.lower() for keyword in ['security', 'encrypt', 'access', 'auth'])
                ]
                recommendations.extend(service_recommendations)
        
        # Add general security recommendations
        general_security = {
            "aws": [
                "Enable AWS CloudTrail for audit logging",
                "Use IAM roles instead of access keys",
                "Enable GuardDuty for threat detection",
                "Implement least privilege access",
                "Enable VPC Flow Logs"
            ],
            "azure": [
                "Enable Azure Security Center",
                "Use Azure AD for identity management",
                "Implement Network Security Groups",
                "Enable Azure Monitor and Log Analytics",
                "Use Azure Key Vault for secrets"
            ],
            "gcp": [
                "Enable Cloud Security Command Center",
                "Use Cloud IAM for access control",
                "Implement VPC firewall rules",
                "Enable Cloud Logging and Monitoring",
                "Use Secret Manager for sensitive data"
            ]
        }
        
        recommendations.extend(general_security.get(provider, []))
        
        return {
            "provider": provider,
            "services": services,
            "recommendations": list(set(recommendations)),  # Remove duplicates
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def get_terraform_examples(
        self, 
        provider: str, 
        services: List[str]
    ) -> Dict[str, Any]:
        """Get Terraform examples via Context7 MCP"""
        
        terraform_examples = {
            "aws": {
                "ec2": '''
resource "aws_instance" "example" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.micro"
  
  vpc_security_group_ids = [aws_security_group.example.id]
  
  tags = {
    Name = "ExampleInstance"
  }
}

resource "aws_security_group" "example" {
  name_prefix = "example-"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
''',
                "rds": '''
resource "aws_db_instance" "example" {
  identifier = "example-database"
  
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "exampledb"
  username = "admin"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  
  tags = {
    Name = "ExampleDatabase"
  }
}
'''
            }
        }
        
        examples = {}
        for service in services:
            if provider in terraform_examples and service in terraform_examples[provider]:
                examples[service] = terraform_examples[provider][service]
        
        return {
            "provider": provider,
            "services": services,
            "examples": examples,
            "generated_at": datetime.utcnow().isoformat()
        }