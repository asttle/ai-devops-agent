#!/usr/bin/env python3
"""
Architect Agent - Designs service mesh, API gateway, and shared services architecture
Implements Azure AKS best practices for networking and service design
"""

import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.network import NetworkManagementClient


@dataclass
class ServiceMeshConfig:
    """Configuration for Istio service mesh on AKS"""
    enable_istio: bool = True
    ingress_gateway_type: str = "LoadBalancer"
    mtls_mode: str = "STRICT"
    telemetry_v2: bool = True
    distributed_tracing: bool = True
    observability_addons: List[str] = None
    
    def __post_init__(self):
        if self.observability_addons is None:
            self.observability_addons = ["kiali", "jaeger", "grafana", "prometheus"]


@dataclass
class APIGatewayConfig:
    """Configuration for Azure Application Gateway with AKS"""
    enable_agic: bool = True  # Application Gateway Ingress Controller
    ssl_termination: bool = True
    waf_enabled: bool = True
    waf_mode: str = "Prevention"
    autoscaling_min_capacity: int = 2
    autoscaling_max_capacity: int = 10
    custom_error_pages: bool = True
    health_probes: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.health_probes is None:
            self.health_probes = [
                {
                    "name": "default-health-probe",
                    "protocol": "Http",
                    "path": "/health",
                    "interval": 30,
                    "timeout": 30,
                    "unhealthy_threshold": 3
                }
            ]


@dataclass
class SharedServicesConfig:
    """Configuration for shared services in AKS cluster"""
    enable_external_dns: bool = True
    enable_cert_manager: bool = True
    enable_nginx_ingress: bool = False  # Using App Gateway instead
    enable_external_secrets: bool = True
    enable_keda: bool = True  # Kubernetes Event-driven Autoscaling
    enable_dapr: bool = True  # Distributed Application Runtime
    logging_solution: str = "azure-monitor"
    metrics_solution: str = "azure-monitor"
    backup_solution: str = "velero"


@dataclass
class NetworkingConfig:
    """Advanced networking configuration for AKS"""
    network_plugin: str = "azure"  # CNI
    network_policy: str = "calico"
    service_cidr: str = "10.0.0.0/16"
    dns_service_ip: str = "10.0.0.10"
    pod_cidr: str = "10.244.0.0/16"
    enable_private_cluster: bool = True
    enable_authorized_ip_ranges: bool = True
    authorized_ip_ranges: List[str] = None
    
    def __post_init__(self):
        if self.authorized_ip_ranges is None:
            self.authorized_ip_ranges = []


class ArchitectAgent:
    """
    Architect Agent responsible for designing and implementing:
    - Service mesh architecture (Istio)
    - API Gateway configuration (Azure Application Gateway + AGIC)
    - Shared services setup
    - Network architecture and security
    """
    
    def __init__(self, subscription_id: str, resource_group: str, location: str = "eastus"):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.location = location
        self.credential = DefaultAzureCredential()
        self.container_client = ContainerServiceClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)
        
        # Initialize configurations
        self.service_mesh_config = ServiceMeshConfig()
        self.api_gateway_config = APIGatewayConfig()
        self.shared_services_config = SharedServicesConfig()
        self.networking_config = NetworkingConfig()
    
    def design_service_mesh_architecture(self) -> Dict[str, Any]:
        """Design Istio service mesh configuration for AKS"""
        istio_config = {
            "apiVersion": "install.istio.io/v1alpha1",
            "kind": "IstioOperator",
            "metadata": {
                "name": "control-plane",
                "namespace": "istio-system"
            },
            "spec": {
                "values": {
                    "global": {
                        "meshID": "mesh1",
                        "multiCluster": {"clusterName": "cluster1"},
                        "network": "network1"
                    }
                },
                "components": {
                    "pilot": {
                        "k8s": {
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "500m", "memory": "512Mi"}
                            }
                        }
                    },
                    "ingressGateways": [{
                        "name": "istio-ingressgateway",
                        "enabled": True,
                        "k8s": {
                            "service": {
                                "type": self.service_mesh_config.ingress_gateway_type,
                                "annotations": {
                                    "service.beta.kubernetes.io/azure-load-balancer-internal": "true"
                                }
                            }
                        }
                    }]
                }
            }
        }
        
        # Add security policies
        security_policies = self._generate_istio_security_policies()
        
        return {
            "istio_operator": istio_config,
            "security_policies": security_policies,
            "telemetry_config": self._generate_telemetry_config()
        }
    
    def design_api_gateway_architecture(self) -> Dict[str, Any]:
        """Design Azure Application Gateway with AGIC configuration"""
        app_gateway_config = {
            "name": f"appgw-{self.resource_group}",
            "location": self.location,
            "sku": {
                "name": "WAF_v2",
                "tier": "WAF_v2",
                "capacity": self.api_gateway_config.autoscaling_min_capacity
            },
            "autoscale_configuration": {
                "min_capacity": self.api_gateway_config.autoscaling_min_capacity,
                "max_capacity": self.api_gateway_config.autoscaling_max_capacity
            },
            "web_application_firewall_configuration": {
                "enabled": self.api_gateway_config.waf_enabled,
                "firewall_mode": self.api_gateway_config.waf_mode,
                "rule_set_type": "OWASP",
                "rule_set_version": "3.2"
            },
            "ssl_certificates": [],
            "frontend_ip_configurations": [
                {
                    "name": "appGwPublicFrontendIp",
                    "public_ip_address": {
                        "id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Network/publicIPAddresses/appgw-pip"
                    }
                }
            ]
        }
        
        agic_config = self._generate_agic_configuration()
        
        return {
            "application_gateway": app_gateway_config,
            "agic_configuration": agic_config,
            "ingress_examples": self._generate_ingress_examples()
        }
    
    def design_shared_services_architecture(self) -> Dict[str, Any]:
        """Design shared services for the AKS cluster"""
        shared_services = {
            "external_dns": self._generate_external_dns_config() if self.shared_services_config.enable_external_dns else None,
            "cert_manager": self._generate_cert_manager_config() if self.shared_services_config.enable_cert_manager else None,
            "external_secrets": self._generate_external_secrets_config() if self.shared_services_config.enable_external_secrets else None,
            "keda": self._generate_keda_config() if self.shared_services_config.enable_keda else None,
            "dapr": self._generate_dapr_config() if self.shared_services_config.enable_dapr else None,
            "velero_backup": self._generate_velero_config() if self.shared_services_config.backup_solution == "velero" else None
        }
        
        return {k: v for k, v in shared_services.items() if v is not None}
    
    def design_network_architecture(self) -> Dict[str, Any]:
        """Design network architecture for AKS cluster"""
        network_config = {
            "virtual_network": {
                "name": f"vnet-{self.resource_group}",
                "address_space": ["10.0.0.0/8"],
                "subnets": [
                    {
                        "name": "aks-subnet",
                        "address_prefix": "10.1.0.0/16",
                        "private_endpoint_network_policies": "Disabled"
                    },
                    {
                        "name": "appgw-subnet",
                        "address_prefix": "10.2.0.0/24"
                    },
                    {
                        "name": "private-endpoints-subnet",
                        "address_prefix": "10.3.0.0/24",
                        "private_endpoint_network_policies": "Enabled"
                    }
                ]
            },
            "network_security_groups": self._generate_nsg_rules(),
            "private_dns_zones": [
                "privatelink.eastus.azmk8s.io",
                "privatelink.blob.core.windows.net",
                "privatelink.table.core.windows.net",
                "privatelink.queue.core.windows.net",
                "privatelink.file.core.windows.net",
                "privatelink.vault.azure.net"
            ]
        }
        
        return network_config
    
    def generate_terraform_templates(self) -> Dict[str, str]:
        """Generate Terraform templates for the complete architecture"""
        templates = {
            "main.tf": self._generate_main_terraform(),
            "variables.tf": self._generate_variables_terraform(),
            "outputs.tf": self._generate_outputs_terraform(),
            "network.tf": self._generate_network_terraform(),
            "aks.tf": self._generate_aks_terraform(),
            "application_gateway.tf": self._generate_appgw_terraform()
        }
        
        return templates
    
    def _generate_istio_security_policies(self) -> List[Dict[str, Any]]:
        """Generate Istio security policies"""
        return [
            {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "PeerAuthentication",
                "metadata": {
                    "name": "default",
                    "namespace": "istio-system"
                },
                "spec": {
                    "mtls": {"mode": self.service_mesh_config.mtls_mode}
                }
            },
            {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "AuthorizationPolicy",
                "metadata": {
                    "name": "deny-all",
                    "namespace": "istio-system"
                },
                "spec": {}
            }
        ]
    
    def _generate_telemetry_config(self) -> Dict[str, Any]:
        """Generate telemetry configuration for Istio"""
        return {
            "apiVersion": "telemetry.istio.io/v1alpha1",
            "kind": "Telemetry",
            "metadata": {
                "name": "metrics",
                "namespace": "istio-system"
            },
            "spec": {
                "metrics": [
                    {
                        "providers": [{"name": "prometheus"}],
                        "overrides": [
                            {
                                "match": {"metric": "ALL_METRICS"},
                                "tags": {
                                    "environment": {"value": "production"},
                                    "cluster": {"value": "aks-cluster"}
                                }
                            }
                        ]
                    }
                ]
            }
        }
    
    def _generate_agic_configuration(self) -> Dict[str, Any]:
        """Generate AGIC (Application Gateway Ingress Controller) configuration"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "azure-application-gateway-ingress-controller",
                "namespace": "kube-system"
            },
            "data": {
                "armAuth.type": "workloadIdentity",
                "armAuth.identityResourceID": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/agic-identity",
                "armAuth.identityClientID": "AGIC_CLIENT_ID_PLACEHOLDER",
                "appgw.subscriptionId": self.subscription_id,
                "appgw.resourceGroup": self.resource_group,
                "appgw.name": f"appgw-{self.resource_group}",
                "appgw.shared": "false",
                "kubernetes.watchNamespace": "",
                "aksClusterConfiguration.apiServerAddress": "AKS_API_SERVER_PLACEHOLDER"
            }
        }
    
    def _generate_ingress_examples(self) -> List[Dict[str, Any]]:
        """Generate example ingress configurations"""
        return [
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": "example-app-ingress",
                    "annotations": {
                        "kubernetes.io/ingress.class": "azure/application-gateway",
                        "appgw.ingress.kubernetes.io/ssl-redirect": "true",
                        "appgw.ingress.kubernetes.io/backend-protocol": "http",
                        "appgw.ingress.kubernetes.io/health-probe-path": "/health"
                    }
                },
                "spec": {
                    "tls": [
                        {
                            "secretName": "example-app-tls",
                            "hosts": ["example-app.domain.com"]
                        }
                    ],
                    "rules": [
                        {
                            "host": "example-app.domain.com",
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": "example-app-service",
                                                "port": {"number": 80}
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    
    def _generate_external_dns_config(self) -> Dict[str, Any]:
        """Generate External DNS configuration for Azure"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "external-dns",
                "namespace": "kube-system"
            },
            "spec": {
                "selector": {"matchLabels": {"app": "external-dns"}},
                "template": {
                    "metadata": {"labels": {"app": "external-dns"}},
                    "spec": {
                        "serviceAccountName": "external-dns",
                        "containers": [
                            {
                                "name": "external-dns",
                                "image": "k8s.gcr.io/external-dns/external-dns:v0.13.1",
                                "args": [
                                    "--source=ingress",
                                    "--source=service",
                                    "--provider=azure",
                                    "--azure-resource-group=" + self.resource_group,
                                    "--azure-subscription-id=" + self.subscription_id,
                                    "--txt-owner-id=aks-cluster"
                                ],
                                "env": [
                                    {
                                        "name": "AZURE_CLIENT_ID",
                                        "valueFrom": {"secretKeyRef": {"name": "azure-config-file", "key": "clientId"}}
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    
    def _generate_cert_manager_config(self) -> Dict[str, Any]:
        """Generate cert-manager configuration"""
        return {
            "clusterIssuer": {
                "apiVersion": "cert-manager.io/v1",
                "kind": "ClusterIssuer",
                "metadata": {"name": "letsencrypt-prod"},
                "spec": {
                    "acme": {
                        "server": "https://acme-v02.api.letsencrypt.org/directory",
                        "email": "admin@domain.com",
                        "privateKeySecretRef": {"name": "letsencrypt-prod"},
                        "solvers": [
                            {
                                "http01": {
                                    "ingress": {
                                        "class": "azure/application-gateway",
                                        "podTemplate": {
                                            "metadata": {
                                                "annotations": {
                                                    "appgw.ingress.kubernetes.io/backend-protocol": "http"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def _generate_external_secrets_config(self) -> Dict[str, Any]:
        """Generate External Secrets Operator configuration for Azure Key Vault"""
        return {
            "secretStore": {
                "apiVersion": "external-secrets.io/v1beta1",
                "kind": "SecretStore",
                "metadata": {
                    "name": "azure-keyvault-store",
                    "namespace": "default"
                },
                "spec": {
                    "provider": {
                        "azurekv": {
                            "vaultUrl": f"https://kv-{self.resource_group}.vault.azure.net/",
                            "authType": "WorkloadIdentity",
                            "serviceAccountRef": {"name": "external-secrets-sa"}
                        }
                    }
                }
            }
        }
    
    def _generate_keda_config(self) -> Dict[str, Any]:
        """Generate KEDA configuration for event-driven autoscaling"""
        return {
            "scaler_example": {
                "apiVersion": "keda.sh/v1alpha1",
                "kind": "ScaledObject",
                "metadata": {
                    "name": "azure-queue-scaler",
                    "namespace": "default"
                },
                "spec": {
                    "scaleTargetRef": {"name": "worker-app"},
                    "minReplicaCount": 1,
                    "maxReplicaCount": 10,
                    "triggers": [
                        {
                            "type": "azure-queue",
                            "metadata": {
                                "queueName": "work-queue",
                                "queueLength": "5"
                            },
                            "authenticationRef": {"name": "azure-queue-auth"}
                        }
                    ]
                }
            }
        }
    
    def _generate_dapr_config(self) -> Dict[str, Any]:
        """Generate Dapr configuration"""
        return {
            "configuration": {
                "apiVersion": "dapr.io/v1alpha1",
                "kind": "Configuration",
                "metadata": {"name": "dapr-config"},
                "spec": {
                    "tracing": {
                        "samplingRate": "1",
                        "zipkin": {"endpointAddress": "http://jaeger-collector:14268/api/traces"}
                    },
                    "features": [{"name": "ServiceInvocation", "enabled": True}]
                }
            }
        }
    
    def _generate_velero_config(self) -> Dict[str, Any]:
        """Generate Velero backup configuration"""
        return {
            "backupStorageLocation": {
                "apiVersion": "velero.io/v1",
                "kind": "BackupStorageLocation",
                "metadata": {"name": "azure"},
                "spec": {
                    "provider": "azure",
                    "objectStorage": {
                        "bucket": f"velero-backups-{self.resource_group}",
                        "prefix": "aks"
                    },
                    "config": {
                        "resourceGroup": self.resource_group,
                        "storageAccount": f"velero{self.resource_group.replace('-', '')}"
                    }
                }
            }
        }
    
    def _generate_nsg_rules(self) -> List[Dict[str, Any]]:
        """Generate Network Security Group rules"""
        return [
            {
                "name": "aks-nsg",
                "rules": [
                    {
                        "name": "AllowHTTPS",
                        "priority": 100,
                        "direction": "Inbound",
                        "access": "Allow",
                        "protocol": "Tcp",
                        "source_port_range": "*",
                        "destination_port_range": "443",
                        "source_address_prefix": "*",
                        "destination_address_prefix": "*"
                    },
                    {
                        "name": "AllowHTTP",
                        "priority": 110,
                        "direction": "Inbound", 
                        "access": "Allow",
                        "protocol": "Tcp",
                        "source_port_range": "*",
                        "destination_port_range": "80",
                        "source_address_prefix": "*",
                        "destination_address_prefix": "*"
                    },
                    {
                        "name": "DenyAllInbound",
                        "priority": 4000,
                        "direction": "Inbound",
                        "access": "Deny",
                        "protocol": "*",
                        "source_port_range": "*",
                        "destination_port_range": "*",
                        "source_address_prefix": "*",
                        "destination_address_prefix": "*"
                    }
                ]
            }
        ]
    
    def _generate_main_terraform(self) -> str:
        """Generate main Terraform configuration"""
        return """
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.aks.kube_config.0.host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = azurerm_kubernetes_cluster.aks.kube_config.0.host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate)
  }
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = var.common_tags
}
"""
    
    def _generate_variables_terraform(self) -> str:
        """Generate Terraform variables"""
        return """
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 3
}

variable "vm_size" {
  description = "Size of the Virtual Machine"
  type        = string
  default     = "Standard_B2s"
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "ai-devops-agent"
    Owner       = "devops-team"
  }
}
"""
    
    def _generate_outputs_terraform(self) -> str:
        """Generate Terraform outputs"""
        return """
output "cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "cluster_endpoint" {
  value = azurerm_kubernetes_cluster.aks.kube_config.0.host
}

output "cluster_ca_certificate" {
  value     = azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate
  sensitive = true
}

output "application_gateway_id" {
  value = azurerm_application_gateway.appgw.id
}

output "virtual_network_id" {
  value = azurerm_virtual_network.main.id
}
"""
    
    def _generate_network_terraform(self) -> str:
        """Generate network Terraform configuration"""
        return """
resource "azurerm_virtual_network" "main" {
  name                = "vnet-${var.cluster_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/8"]

  tags = var.common_tags
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.1.0.0/16"]

  private_endpoint_network_policies_enabled = false
}

resource "azurerm_subnet" "appgw" {
  name                 = "appgw-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.2.0.0/24"]
}

resource "azurerm_network_security_group" "aks" {
  name                = "nsg-${var.cluster_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.common_tags
}

resource "azurerm_subnet_network_security_group_association" "aks" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks.id
}
"""
    
    def _generate_aks_terraform(self) -> str:
        """Generate AKS Terraform configuration"""
        return """
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.cluster_name
  kubernetes_version  = var.kubernetes_version

  private_cluster_enabled = true
  
  default_node_pool {
    name           = "default"
    node_count     = var.node_count
    vm_size        = var.vm_size
    vnet_subnet_id = azurerm_subnet.aks.id
    
    enable_auto_scaling = true
    min_count          = 1
    max_count          = 5
    
    upgrade_settings {
      max_surge = "10%"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin     = "azure"
    network_policy     = "calico"
    service_cidr       = "10.0.0.0/16"
    dns_service_ip     = "10.0.0.10"
    load_balancer_sku  = "standard"
  }

  ingress_application_gateway {
    gateway_id = azurerm_application_gateway.appgw.id
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  azure_policy_enabled = true

  tags = var.common_tags
}

resource "azurerm_kubernetes_cluster_node_pool" "spot" {
  name                  = "spot"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size              = "Standard_B2s"
  node_count           = 2
  vnet_subnet_id       = azurerm_subnet.aks.id
  
  priority        = "Spot"
  eviction_policy = "Delete"
  spot_max_price  = -1
  
  node_taints = [
    "kubernetes.azure.com/scalesetpriority=spot:NoSchedule"
  ]
  
  node_labels = {
    "kubernetes.azure.com/scalesetpriority" = "spot"
  }

  tags = var.common_tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.cluster_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = var.common_tags
}
"""
    
    def _generate_appgw_terraform(self) -> str:
        """Generate Application Gateway Terraform configuration"""
        return """
resource "azurerm_public_ip" "appgw" {
  name                = "pip-appgw-${var.cluster_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.common_tags
}

resource "azurerm_application_gateway" "appgw" {
  name                = "appgw-${var.cluster_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }

  autoscale_configuration {
    min_capacity = 2
    max_capacity = 10
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }

  gateway_ip_configuration {
    name      = "appGatewayIpConfig"
    subnet_id = azurerm_subnet.appgw.id
  }

  frontend_port {
    name = "port_80"
    port = 80
  }

  frontend_port {
    name = "port_443"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "appGwPublicFrontendIp"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }

  backend_address_pool {
    name = "defaultaddresspool"
  }

  backend_http_settings {
    name                  = "defaulthttpsetting"
    cookie_based_affinity = "Disabled"
    path                  = "/"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 20
  }

  http_listener {
    name                           = "defaulthttplistener"
    frontend_ip_configuration_name = "appGwPublicFrontendIp"
    frontend_port_name             = "port_80"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "defaultrule"
    rule_type                  = "Basic"
    http_listener_name         = "defaulthttplistener"
    backend_address_pool_name  = "defaultaddresspool"
    backend_http_settings_name = "defaulthttpsetting"
    priority                   = 1
  }

  tags = var.common_tags
}
"""

    def execute_architecture_design(self) -> Dict[str, Any]:
        """Execute the complete architecture design process"""
        architecture = {
            "service_mesh": self.design_service_mesh_architecture(),
            "api_gateway": self.design_api_gateway_architecture(), 
            "shared_services": self.design_shared_services_architecture(),
            "network": self.design_network_architecture(),
            "terraform_templates": self.generate_terraform_templates()
        }
        
        return architecture


def main():
    """Main execution function for testing"""
    agent = ArchitectAgent(
        subscription_id="your-subscription-id",
        resource_group="rg-aks-demo",
        location="eastus"
    )
    
    architecture = agent.execute_architecture_design()
    
    # Save configurations to files
    with open("service_mesh_config.yaml", "w") as f:
        yaml.dump(architecture["service_mesh"], f, default_flow_style=False)
    
    with open("api_gateway_config.yaml", "w") as f:
        yaml.dump(architecture["api_gateway"], f, default_flow_style=False)
    
    print("Architecture design completed successfully!")
    print(f"Generated configurations for:")
    print(f"- Service Mesh (Istio)")
    print(f"- API Gateway (Azure Application Gateway + AGIC)")
    print(f"- Shared Services (External DNS, Cert Manager, KEDA, Dapr, etc.)")
    print(f"- Network Architecture")
    print(f"- Complete Terraform templates")


if __name__ == "__main__":
    main()