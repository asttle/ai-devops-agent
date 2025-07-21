#!/usr/bin/env python3
"""
Security Agent - Implements zero-trust networking, secret management, and security best practices
Focuses on Azure security services, compliance, and hardening for AKS clusters
"""

import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.security import SecurityCenter
from azure.mgmt.policyinsights import PolicyInsightsClient


@dataclass
class ZeroTrustConfig:
    """Zero Trust network security configuration"""
    enable_network_policies: bool = True
    enable_pod_security_standards: bool = True
    enable_admission_controller: bool = True
    enable_image_scanning: bool = True
    enable_runtime_protection: bool = True
    default_deny_all: bool = True
    microsegmentation: bool = True
    identity_verification: bool = True
    
    
@dataclass
class SecretManagementConfig:
    """Azure Key Vault and secret management configuration"""
    enable_key_vault_csi: bool = True
    enable_workload_identity: bool = True
    enable_pod_identity: bool = False  # Legacy, prefer workload identity
    key_vault_name: str = ""
    enable_cert_manager_integration: bool = True
    enable_external_secrets: bool = True
    secret_rotation_days: int = 90
    enable_secret_encryption: bool = True


@dataclass
class ComplianceConfig:
    """Compliance and governance configuration"""
    enable_azure_policy: bool = True
    enable_azure_defender: bool = True
    enable_regulatory_compliance: bool = True
    compliance_standards: List[str] = None
    enable_vulnerability_assessment: bool = True
    enable_security_center: bool = True
    enable_sentinel_integration: bool = True
    
    def __post_init__(self):
        if self.compliance_standards is None:
            self.compliance_standards = ["PCI-DSS", "SOC2", "ISO27001", "CIS"]


@dataclass
class IdentityConfig:
    """Identity and access management configuration"""
    enable_azure_ad_integration: bool = True
    enable_rbac: bool = True
    enable_pod_managed_identity: bool = True
    enable_workload_identity: bool = True
    admin_group_object_ids: List[str] = None
    enable_local_accounts: bool = False
    enable_azure_ad_pod_identity: bool = False  # Deprecated
    
    def __post_init__(self):
        if self.admin_group_object_ids is None:
            self.admin_group_object_ids = []


class SecurityAgent:
    """
    Security Agent responsible for implementing:
    - Zero-trust networking and microsegmentation
    - Azure Key Vault integration and secret management
    - Security policies and compliance
    - Identity and access management
    - Security monitoring and threat detection
    """
    
    def __init__(self, subscription_id: str, resource_group: str, location: str = "eastus"):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.location = location
        self.credential = DefaultAzureCredential()
        
        # Initialize Azure clients
        self.container_client = ContainerServiceClient(self.credential, subscription_id)
        self.keyvault_client = KeyVaultManagementClient(self.credential, subscription_id)
        self.security_client = SecurityCenter(self.credential, subscription_id)
        self.policy_client = PolicyInsightsClient(self.credential)
        
        # Initialize configurations
        self.zero_trust_config = ZeroTrustConfig()
        self.secret_mgmt_config = SecretManagementConfig(key_vault_name=f"kv-{resource_group}")
        self.compliance_config = ComplianceConfig()
        self.identity_config = IdentityConfig()
    
    def implement_zero_trust_networking(self) -> Dict[str, Any]:
        """Implement zero-trust network security policies"""
        zero_trust_policies = {
            "network_policies": self._generate_network_policies(),
            "pod_security_policies": self._generate_pod_security_policies(),
            "admission_controllers": self._generate_admission_controller_config(),
            "service_mesh_security": self._generate_service_mesh_security(),
            "egress_policies": self._generate_egress_policies()
        }
        
        return zero_trust_policies
    
    def implement_secret_management(self) -> Dict[str, Any]:
        """Implement Azure Key Vault integration and secret management"""
        secret_management = {
            "key_vault_configuration": self._generate_key_vault_config(),
            "csi_driver_config": self._generate_key_vault_csi_config(),
            "workload_identity_config": self._generate_workload_identity_config(),
            "external_secrets_config": self._generate_external_secrets_config(),
            "cert_manager_integration": self._generate_cert_manager_keyvault_config(),
            "secret_rotation_policies": self._generate_secret_rotation_policies()
        }
        
        return secret_management
    
    def implement_compliance_governance(self) -> Dict[str, Any]:
        """Implement Azure Policy and compliance controls"""
        compliance = {
            "azure_policies": self._generate_azure_policies(),
            "security_baseline": self._generate_security_baseline(),
            "cis_benchmark": self._generate_cis_benchmark_policies(),
            "regulatory_compliance": self._generate_regulatory_compliance(),
            "vulnerability_management": self._generate_vulnerability_management()
        }
        
        return compliance
    
    def implement_identity_access_management(self) -> Dict[str, Any]:
        """Implement Azure AD integration and RBAC"""
        iam = {
            "azure_ad_integration": self._generate_azure_ad_integration(),
            "rbac_configurations": self._generate_rbac_configurations(),
            "cluster_roles": self._generate_cluster_roles(),
            "workload_identity_setup": self._generate_workload_identity_setup(),
            "service_accounts": self._generate_service_accounts()
        }
        
        return iam
    
    def implement_security_monitoring(self) -> Dict[str, Any]:
        """Implement security monitoring and threat detection"""
        monitoring = {
            "azure_defender_config": self._generate_azure_defender_config(),
            "security_center_config": self._generate_security_center_config(),
            "sentinel_integration": self._generate_sentinel_integration(),
            "audit_logging": self._generate_audit_logging_config(),
            "security_alerts": self._generate_security_alerts()
        }
        
        return monitoring
    
    def _generate_network_policies(self) -> List[Dict[str, Any]]:
        """Generate Kubernetes Network Policies for microsegmentation"""
        return [
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "deny-all-ingress",
                    "namespace": "default"
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Ingress"]
                }
            },
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "deny-all-egress",
                    "namespace": "default"
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Egress"]
                }
            },
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "allow-frontend-to-backend",
                    "namespace": "default"
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": {"app": "backend"}
                    },
                    "policyTypes": ["Ingress"],
                    "ingress": [{
                        "from": [{
                            "podSelector": {
                                "matchLabels": {"app": "frontend"}
                            }
                        }],
                        "ports": [{
                            "protocol": "TCP",
                            "port": 8080
                        }]
                    }]
                }
            },
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "allow-dns-egress",
                    "namespace": "default"
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Egress"],
                    "egress": [{
                        "to": [{
                            "namespaceSelector": {
                                "matchLabels": {"name": "kube-system"}
                            },
                            "podSelector": {
                                "matchLabels": {"k8s-app": "kube-dns"}
                            }
                        }],
                        "ports": [{
                            "protocol": "UDP",
                            "port": 53
                        }]
                    }]
                }
            }
        ]
    
    def _generate_pod_security_policies(self) -> List[Dict[str, Any]]:
        """Generate Pod Security Standards and policies"""
        return [
            {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": "secure-namespace",
                    "labels": {
                        "pod-security.kubernetes.io/enforce": "restricted",
                        "pod-security.kubernetes.io/audit": "restricted",
                        "pod-security.kubernetes.io/warn": "restricted"
                    }
                }
            },
            {
                "apiVersion": "policy/v1beta1",
                "kind": "PodSecurityPolicy",
                "metadata": {"name": "restricted-psp"},
                "spec": {
                    "privileged": False,
                    "allowPrivilegeEscalation": False,
                    "requiredDropCapabilities": ["ALL"],
                    "volumes": ["configMap", "emptyDir", "projected", "secret", "downwardAPI", "persistentVolumeClaim"],
                    "runAsUser": {"rule": "MustRunAsNonRoot"},
                    "runAsGroup": {"rule": "MustRunAs", "ranges": [{"min": 1, "max": 65535}]},
                    "seLinux": {"rule": "RunAsAny"},
                    "fsGroup": {"rule": "RunAsAny"},
                    "readOnlyRootFilesystem": True,
                    "seccompProfile": {"type": "RuntimeDefault"},
                    "supplementalGroups": {"rule": "MustRunAs", "ranges": [{"min": 1, "max": 65535}]}
                }
            }
        ]
    
    def _generate_admission_controller_config(self) -> Dict[str, Any]:
        """Generate OPA Gatekeeper admission controller configuration"""
        return {
            "constraint_template": {
                "apiVersion": "templates.gatekeeper.sh/v1beta1",
                "kind": "ConstraintTemplate",
                "metadata": {"name": "requiredlabels"},
                "spec": {
                    "crd": {
                        "spec": {
                            "names": {"kind": "RequiredLabels"},
                            "validation": {
                                "openAPIV3Schema": {
                                    "type": "object",
                                    "properties": {
                                        "labels": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "targets": [{
                        "target": "admission.k8s.gatekeeper.sh",
                        "rego": """
package requiredlabels

violation[{"msg": msg}] {
    required := input.parameters.labels
    provided := input.review.object.metadata.labels
    missing := required[_]
    not provided[missing]
    msg := sprintf("Missing required label: %v", [missing])
}
"""
                    }]
                }
            },
            "constraint": {
                "apiVersion": "constraints.gatekeeper.sh/v1beta1",
                "kind": "RequiredLabels",
                "metadata": {"name": "must-have-environment"},
                "spec": {
                    "match": {
                        "kinds": [{"apiGroups": ["apps"], "kinds": ["Deployment"]}]
                    },
                    "parameters": {
                        "labels": ["environment", "owner", "cost-center"]
                    }
                }
            }
        }
    
    def _generate_service_mesh_security(self) -> List[Dict[str, Any]]:
        """Generate Istio service mesh security configurations"""
        return [
            {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "PeerAuthentication",
                "metadata": {
                    "name": "default",
                    "namespace": "istio-system"
                },
                "spec": {"mtls": {"mode": "STRICT"}}
            },
            {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "AuthorizationPolicy",
                "metadata": {
                    "name": "frontend-policy",
                    "namespace": "default"
                },
                "spec": {
                    "selector": {"matchLabels": {"app": "frontend"}},
                    "rules": [{
                        "from": [{
                            "source": {"principals": ["cluster.local/ns/istio-system/sa/istio-ingressgateway-service-account"]}
                        }],
                        "to": [{
                            "operation": {"methods": ["GET", "POST"]}
                        }]
                    }]
                }
            },
            {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "RequestAuthentication",
                "metadata": {
                    "name": "jwt-auth",
                    "namespace": "default"
                },
                "spec": {
                    "selector": {"matchLabels": {"app": "backend"}},
                    "jwtRules": [{
                        "issuer": "https://login.microsoftonline.com/tenant-id/v2.0",
                        "jwksUri": "https://login.microsoftonline.com/tenant-id/discovery/v2.0/keys",
                        "audiences": ["api://backend-api"]
                    }]
                }
            }
        ]
    
    def _generate_egress_policies(self) -> List[Dict[str, Any]]:
        """Generate egress network policies for external access control"""
        return [
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "allow-azure-services-egress",
                    "namespace": "default"
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": ["Egress"],
                    "egress": [{
                        "to": [{
                            "namespaceSelector": {},
                            "podSelector": {}
                        }],
                        "ports": [{
                            "protocol": "TCP",
                            "port": 443
                        }]
                    }]
                }
            },
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "allow-keyvault-egress",
                    "namespace": "default"
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": {"access": "keyvault"}
                    },
                    "policyTypes": ["Egress"],
                    "egress": [{
                        "to": [],
                        "ports": [{
                            "protocol": "TCP",
                            "port": 443
                        }]
                    }]
                }
            }
        ]
    
    def _generate_key_vault_config(self) -> Dict[str, Any]:
        """Generate Azure Key Vault configuration"""
        return {
            "key_vault": {
                "name": self.secret_mgmt_config.key_vault_name,
                "location": self.location,
                "sku": "premium",
                "tenant_id": "tenant-id-placeholder",
                "enabled_for_disk_encryption": True,
                "enabled_for_template_deployment": True,
                "enabled_for_deployment": True,
                "enable_rbac_authorization": True,
                "purge_protection_enabled": True,
                "soft_delete_retention_days": 90,
                "network_acls": {
                    "default_action": "Deny",
                    "bypass": "AzureServices",
                    "ip_rules": [],
                    "virtual_network_subnet_ids": []
                }
            },
            "private_endpoint": {
                "name": f"pe-{self.secret_mgmt_config.key_vault_name}",
                "subnet_id": "/subscriptions/subscription-id/resourceGroups/rg/providers/Microsoft.Network/virtualNetworks/vnet/subnets/pe-subnet",
                "private_service_connection": {
                    "name": f"psc-{self.secret_mgmt_config.key_vault_name}",
                    "subresource_names": ["vault"]
                }
            }
        }
    
    def _generate_key_vault_csi_config(self) -> Dict[str, Any]:
        """Generate Key Vault CSI driver configuration"""
        return {
            "secret_provider_class": {
                "apiVersion": "secrets-store.csi.x-k8s.io/v1",
                "kind": "SecretProviderClass",
                "metadata": {
                    "name": "azure-keyvault-secrets",
                    "namespace": "default"
                },
                "spec": {
                    "provider": "azure",
                    "parameters": {
                        "usePodIdentity": "false",
                        "useVMManagedIdentity": "false",
                        "userAssignedIdentityID": "workload-identity-client-id",
                        "keyvaultName": self.secret_mgmt_config.key_vault_name,
                        "tenantId": "tenant-id-placeholder",
                        "objects": json.dumps({
                            "array": [
                                {
                                    "objectName": "database-password",
                                    "objectType": "secret",
                                    "objectVersion": ""
                                },
                                {
                                    "objectName": "api-key",
                                    "objectType": "secret",
                                    "objectVersion": ""
                                }
                            ]
                        })
                    },
                    "secretObjects": [
                        {
                            "secretName": "app-secrets",
                            "type": "Opaque",
                            "data": [
                                {
                                    "objectName": "database-password",
                                    "key": "db_password"
                                },
                                {
                                    "objectName": "api-key",
                                    "key": "api_key"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    
    def _generate_workload_identity_config(self) -> Dict[str, Any]:
        """Generate Workload Identity configuration"""
        return {
            "user_assigned_identity": {
                "name": "workload-identity",
                "resource_group": self.resource_group,
                "location": self.location
            },
            "federated_identity": {
                "name": "federated-identity",
                "resource_group": self.resource_group,
                "parent_id": "user-assigned-identity-id",
                "subject": "system:serviceaccount:default:workload-identity-sa",
                "issuer": "https://oidc.prod-aks.azure.com/tenant-id/",
                "audiences": ["api://AzureADTokenExchange"]
            },
            "service_account": {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": "workload-identity-sa",
                    "namespace": "default",
                    "annotations": {
                        "azure.workload.identity/client-id": "workload-identity-client-id"
                    },
                    "labels": {
                        "azure.workload.identity/use": "true"
                    }
                }
            },
            "deployment_example": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "workload-identity-app",
                    "namespace": "default"
                },
                "spec": {
                    "selector": {"matchLabels": {"app": "workload-identity-app"}},
                    "template": {
                        "metadata": {
                            "labels": {"app": "workload-identity-app"}
                        },
                        "spec": {
                            "serviceAccountName": "workload-identity-sa",
                            "containers": [{
                                "name": "app",
                                "image": "nginx:latest",
                                "volumeMounts": [{
                                    "name": "secrets-store",
                                    "mountPath": "/mnt/secrets",
                                    "readOnly": True
                                }]
                            }],
                            "volumes": [{
                                "name": "secrets-store",
                                "csi": {
                                    "driver": "secrets-store.csi.k8s.io",
                                    "readOnly": True,
                                    "volumeAttributes": {
                                        "secretProviderClass": "azure-keyvault-secrets"
                                    }
                                }
                            }]
                        }
                    }
                }
            }
        }
    
    def _generate_external_secrets_config(self) -> Dict[str, Any]:
        """Generate External Secrets Operator configuration"""
        return {
            "secret_store": {
                "apiVersion": "external-secrets.io/v1beta1",
                "kind": "SecretStore",
                "metadata": {
                    "name": "azure-keyvault-store",
                    "namespace": "default"
                },
                "spec": {
                    "provider": {
                        "azurekv": {
                            "vaultUrl": f"https://{self.secret_mgmt_config.key_vault_name}.vault.azure.net/",
                            "authType": "WorkloadIdentity",
                            "serviceAccountRef": {"name": "external-secrets-sa"}
                        }
                    }
                }
            },
            "external_secret": {
                "apiVersion": "external-secrets.io/v1beta1",
                "kind": "ExternalSecret",
                "metadata": {
                    "name": "app-secrets",
                    "namespace": "default"
                },
                "spec": {
                    "refreshInterval": "5m",
                    "secretStoreRef": {
                        "name": "azure-keyvault-store",
                        "kind": "SecretStore"
                    },
                    "target": {
                        "name": "app-secrets",
                        "creationPolicy": "Owner"
                    },
                    "data": [
                        {
                            "secretKey": "database-password",
                            "remoteRef": {
                                "key": "database-password"
                            }
                        },
                        {
                            "secretKey": "api-key",
                            "remoteRef": {
                                "key": "api-key"
                            }
                        }
                    ]
                }
            }
        }
    
    def _generate_cert_manager_keyvault_config(self) -> Dict[str, Any]:
        """Generate cert-manager integration with Key Vault"""
        return {
            "cluster_issuer": {
                "apiVersion": "cert-manager.io/v1",
                "kind": "ClusterIssuer",
                "metadata": {"name": "keyvault-issuer"},
                "spec": {
                    "azureKeyVault": {
                        "vaultURL": f"https://{self.secret_mgmt_config.key_vault_name}.vault.azure.net/",
                        "certificateName": "wildcard-certificate",
                        "auth": {
                            "workloadIdentity": {
                                "managedIdentityClientId": "workload-identity-client-id"
                            }
                        }
                    }
                }
            }
        }
    
    def _generate_secret_rotation_policies(self) -> List[Dict[str, Any]]:
        """Generate secret rotation policies and automation"""
        return [
            {
                "apiVersion": "v1",
                "kind": "CronJob",
                "metadata": {
                    "name": "secret-rotation",
                    "namespace": "kube-system"
                },
                "spec": {
                    "schedule": "0 2 * * 0",  # Weekly on Sunday at 2 AM
                    "jobTemplate": {
                        "spec": {
                            "template": {
                                "spec": {
                                    "restartPolicy": "OnFailure",
                                    "containers": [{
                                        "name": "secret-rotator",
                                        "image": "azure-secret-rotator:latest",
                                        "command": ["/bin/sh"],
                                        "args": [
                                            "-c",
                                            "echo 'Rotating secrets...' && /app/rotate-secrets.sh"
                                        ],
                                        "env": [
                                            {
                                                "name": "KEY_VAULT_NAME",
                                                "value": self.secret_mgmt_config.key_vault_name
                                            },
                                            {
                                                "name": "ROTATION_DAYS",
                                                "value": str(self.secret_mgmt_config.secret_rotation_days)
                                            }
                                        ]
                                    }]
                                }
                            }
                        }
                    }
                }
            }
        ]
    
    def _generate_azure_policies(self) -> List[Dict[str, Any]]:
        """Generate Azure Policy definitions for AKS security"""
        return [
            {
                "type": "Microsoft.Authorization/policyDefinitions",
                "name": "aks-require-network-policy",
                "properties": {
                    "displayName": "AKS clusters should have network policy enabled",
                    "description": "Network policy should be enabled on AKS clusters to secure network traffic",
                    "mode": "Indexed",
                    "policyRule": {
                        "if": {
                            "allOf": [
                                {
                                    "field": "type",
                                    "equals": "Microsoft.ContainerService/managedClusters"
                                },
                                {
                                    "anyOf": [
                                        {
                                            "field": "Microsoft.ContainerService/managedClusters/networkProfile.networkPolicy",
                                            "exists": "false"
                                        },
                                        {
                                            "field": "Microsoft.ContainerService/managedClusters/networkProfile.networkPolicy",
                                            "notEquals": "calico"
                                        }
                                    ]
                                }
                            ]
                        },
                        "then": {"effect": "deny"}
                    }
                }
            },
            {
                "type": "Microsoft.Authorization/policyDefinitions",
                "name": "aks-require-private-cluster",
                "properties": {
                    "displayName": "AKS clusters should be private",
                    "description": "AKS clusters should be configured as private clusters",
                    "mode": "Indexed",
                    "policyRule": {
                        "if": {
                            "allOf": [
                                {
                                    "field": "type",
                                    "equals": "Microsoft.ContainerService/managedClusters"
                                },
                                {
                                    "field": "Microsoft.ContainerService/managedClusters/apiServerAccessProfile.enablePrivateCluster",
                                    "notEquals": True
                                }
                            ]
                        },
                        "then": {"effect": "deny"}
                    }
                }
            }
        ]
    
    def _generate_security_baseline(self) -> Dict[str, Any]:
        """Generate Azure Security Baseline configuration"""
        return {
            "baseline_policies": [
                "AKS clusters should use managed identities",
                "AKS clusters should have Azure Defender enabled",
                "AKS clusters should disable local admin account",
                "AKS clusters should use Azure AD integration",
                "AKS clusters should have network policy enabled",
                "AKS clusters should be private",
                "AKS clusters should have authorized IP ranges defined",
                "Container images should be deployed from trusted registries only"
            ],
            "security_controls": {
                "network_security": ["NSG rules", "Private endpoints", "Network policies"],
                "identity_access": ["Azure AD integration", "RBAC", "Managed identities"],
                "data_protection": ["Encryption at rest", "Encryption in transit", "Key management"],
                "monitoring": ["Azure Monitor", "Azure Security Center", "Log Analytics"]
            }
        }
    
    def _generate_cis_benchmark_policies(self) -> List[Dict[str, Any]]:
        """Generate CIS Kubernetes Benchmark policies"""
        return [
            {
                "name": "CIS-1.1.1-Master-Node-Configuration",
                "description": "Ensure that the API server pod specification file permissions are set to 644 or more restrictive",
                "category": "Master Node Configuration Files"
            },
            {
                "name": "CIS-1.2.1-API-Server",
                "description": "Ensure that the --anonymous-auth argument is set to false",
                "category": "API Server"
            },
            {
                "name": "CIS-1.3.1-Controller-Manager",
                "description": "Ensure that the --terminated-pod-gc-threshold argument is set as appropriate",
                "category": "Controller Manager"
            },
            {
                "name": "CIS-1.4.1-Scheduler",
                "description": "Ensure that the --profiling argument is set to false",
                "category": "Scheduler"
            },
            {
                "name": "CIS-2.1-etcd",
                "description": "Ensure that the --cert-file and --key-file arguments are set as appropriate",
                "category": "etcd"
            }
        ]
    
    def _generate_regulatory_compliance(self) -> Dict[str, Any]:
        """Generate regulatory compliance configurations"""
        return {
            "pci_dss": {
                "requirements": [
                    "PCI DSS 1.1 - Firewall configuration standards",
                    "PCI DSS 2.1 - Change default passwords",
                    "PCI DSS 3.4 - Encryption of cardholder data",
                    "PCI DSS 8.1 - User access management",
                    "PCI DSS 10.1 - Audit trails"
                ],
                "controls": ["Network segmentation", "Access controls", "Encryption", "Logging"]
            },
            "soc2": {
                "trust_principles": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
                "controls": ["Access controls", "System monitoring", "Change management", "Risk management"]
            },
            "iso27001": {
                "domains": ["Information security policies", "Access control", "Cryptography", "Operations security"],
                "controls": ["Risk assessment", "Security policies", "Access management", "Incident response"]
            }
        }
    
    def _generate_vulnerability_management(self) -> Dict[str, Any]:
        """Generate vulnerability management configuration"""
        return {
            "image_scanning": {
                "registry_scanning": True,
                "runtime_scanning": True,
                "policy": "block_critical_vulnerabilities",
                "scan_frequency": "daily"
            },
            "security_policies": {
                "pod_security_standards": "restricted",
                "network_policies": "enabled",
                "admission_controllers": "enabled"
            },
            "compliance_scanning": {
                "cis_benchmark": True,
                "nsa_hardening_guide": True,
                "custom_policies": True
            }
        }
    
    def _generate_azure_ad_integration(self) -> Dict[str, Any]:
        """Generate Azure AD integration configuration"""
        return {
            "aks_aad_config": {
                "managed": True,
                "enable_azure_rbac": True,
                "admin_group_object_ids": self.identity_config.admin_group_object_ids,
                "tenant_id": "tenant-id-placeholder"
            },
            "cluster_role_bindings": [
                {
                    "apiVersion": "rbac.authorization.k8s.io/v1",
                    "kind": "ClusterRoleBinding",
                    "metadata": {"name": "aks-cluster-admins"},
                    "roleRef": {
                        "apiGroup": "rbac.authorization.k8s.io",
                        "kind": "ClusterRole",
                        "name": "cluster-admin"
                    },
                    "subjects": [{
                        "apiGroup": "rbac.authorization.k8s.io",
                        "kind": "Group",
                        "name": "admin-group-object-id"
                    }]
                }
            ]
        }
    
    def _generate_rbac_configurations(self) -> List[Dict[str, Any]]:
        """Generate RBAC configurations for different roles"""
        return [
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {"name": "developer-role"},
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["pods", "services", "configmaps", "secrets"],
                        "verbs": ["get", "list", "create", "update", "patch", "delete"]
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["deployments", "replicasets"],
                        "verbs": ["get", "list", "create", "update", "patch", "delete"]
                    }
                ]
            },
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {"name": "viewer-role"},
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["pods", "services", "configmaps"],
                        "verbs": ["get", "list"]
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["deployments", "replicasets"],
                        "verbs": ["get", "list"]
                    }
                ]
            }
        ]
    
    def _generate_cluster_roles(self) -> List[Dict[str, Any]]:
        """Generate custom cluster roles for specific use cases"""
        return [
            {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {"name": "security-scanner"},
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["pods", "services", "namespaces"],
                        "verbs": ["get", "list"]
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["deployments", "daemonsets", "statefulsets"],
                        "verbs": ["get", "list"]
                    },
                    {
                        "apiGroups": ["networking.k8s.io"],
                        "resources": ["networkpolicies"],
                        "verbs": ["get", "list"]
                    }
                ]
            }
        ]
    
    def _generate_workload_identity_setup(self) -> Dict[str, Any]:
        """Generate complete workload identity setup"""
        return {
            "oidc_issuer": "https://oidc.prod-aks.azure.com/tenant-id/",
            "user_assigned_identities": [
                {
                    "name": "keyvault-reader-identity",
                    "permissions": ["Key Vault Secrets User"],
                    "federated_subjects": ["system:serviceaccount:default:keyvault-reader-sa"]
                },
                {
                    "name": "storage-access-identity",
                    "permissions": ["Storage Blob Data Reader"],
                    "federated_subjects": ["system:serviceaccount:default:storage-access-sa"]
                }
            ]
        }
    
    def _generate_service_accounts(self) -> List[Dict[str, Any]]:
        """Generate service accounts with workload identity"""
        return [
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": "keyvault-reader-sa",
                    "namespace": "default",
                    "annotations": {
                        "azure.workload.identity/client-id": "keyvault-reader-client-id"
                    },
                    "labels": {
                        "azure.workload.identity/use": "true"
                    }
                }
            },
            {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": "storage-access-sa",
                    "namespace": "default",
                    "annotations": {
                        "azure.workload.identity/client-id": "storage-access-client-id"
                    },
                    "labels": {
                        "azure.workload.identity/use": "true"
                    }
                }
            }
        ]
    
    def _generate_azure_defender_config(self) -> Dict[str, Any]:
        """Generate Azure Defender configuration"""
        return {
            "defender_plans": [
                {"resource_type": "Containers", "pricing_tier": "Standard"},
                {"resource_type": "Kubernetes", "pricing_tier": "Standard"},
                {"resource_type": "ContainerRegistry", "pricing_tier": "Standard"}
            ],
            "security_contacts": [{
                "email": "security@company.com",
                "phone": "+1234567890",
                "alert_notifications": True,
                "alerts_to_admins": True
            }]
        }
    
    def _generate_security_center_config(self) -> Dict[str, Any]:
        """Generate Azure Security Center configuration"""
        return {
            "auto_provisioning": {
                "log_analytics_agent": "On",
                "vulnerability_assessment": "On",
                "microsoft_defender_for_containers": "On"
            },
            "security_policies": {
                "kubernetes_service_should_be_upgraded": True,
                "pod_security_policies_should_be_defined": True,
                "role_based_access_control_should_be_used": True
            }
        }
    
    def _generate_sentinel_integration(self) -> Dict[str, Any]:
        """Generate Azure Sentinel integration"""
        return {
            "data_connectors": [
                "Azure Activity",
                "Azure Kubernetes Service",
                "Microsoft Defender for Cloud",
                "Azure Key Vault"
            ],
            "analytic_rules": [
                "Suspicious kubectl commands",
                "Privilege escalation attempts",
                "Unusual network traffic patterns",
                "Failed authentication attempts"
            ]
        }
    
    def _generate_audit_logging_config(self) -> Dict[str, Any]:
        """Generate audit logging configuration"""
        return {
            "audit_policy": {
                "apiVersion": "audit.k8s.io/v1",
                "kind": "Policy",
                "rules": [
                    {
                        "level": "RequestResponse",
                        "resources": [{"group": "", "resources": ["secrets"]}]
                    },
                    {
                        "level": "Request",
                        "resources": [{"group": "rbac.authorization.k8s.io", "resources": ["*"]}]
                    },
                    {
                        "level": "Metadata",
                        "resources": [{"group": "", "resources": ["*"]}]
                    }
                ]
            },
            "log_analytics_integration": True
        }
    
    def _generate_security_alerts(self) -> List[Dict[str, Any]]:
        """Generate security alert configurations"""
        return [
            {
                "alert_name": "Privileged Container Detected",
                "severity": "High",
                "description": "A container running in privileged mode was detected",
                "query": "SecurityEvent | where EventID == 4648 and TargetUserName contains 'privileged'"
            },
            {
                "alert_name": "Suspicious Network Activity",
                "severity": "Medium",
                "description": "Unusual network traffic patterns detected",
                "query": "NetworkMonitoring | where BytesReceived > 10000000"
            },
            {
                "alert_name": "Failed Authentication Attempts",
                "severity": "Medium",
                "description": "Multiple failed authentication attempts detected",
                "query": "SigninLogs | where ResultType != '0' | summarize count() by UserPrincipalName"
            }
        ]
    
    def generate_security_terraform_templates(self) -> Dict[str, str]:
        """Generate Terraform templates for security components"""
        return {
            "security_main.tf": self._generate_security_terraform(),
            "key_vault.tf": self._generate_key_vault_terraform(),
            "azure_policy.tf": self._generate_policy_terraform(),
            "security_center.tf": self._generate_security_center_terraform()
        }
    
    def _generate_security_terraform(self) -> str:
        """Generate main security Terraform configuration"""
        return """
# Azure Key Vault for secrets management
resource "azurerm_key_vault" "main" {
  name                       = var.key_vault_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "premium"
  
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  enabled_for_deployment         = true
  enable_rbac_authorization      = true
  purge_protection_enabled       = true
  soft_delete_retention_days     = 90

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }

  tags = var.common_tags
}

# Private endpoint for Key Vault
resource "azurerm_private_endpoint" "keyvault" {
  name                = "pe-${var.key_vault_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoints_subnet_id

  private_service_connection {
    name                           = "psc-${var.key_vault_name}"
    private_connection_resource_id = azurerm_key_vault.main.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }

  tags = var.common_tags
}

# User assigned identity for workload identity
resource "azurerm_user_assigned_identity" "workload_identity" {
  name                = "workload-identity"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.common_tags
}

# Role assignment for Key Vault access
resource "azurerm_role_assignment" "keyvault_secrets_user" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.workload_identity.principal_id
}

# Federated identity credential
resource "azurerm_federated_identity_credential" "main" {
  name                = "federated-identity"
  resource_group_name = var.resource_group_name
  parent_id           = azurerm_user_assigned_identity.workload_identity.id
  subject             = "system:serviceaccount:default:workload-identity-sa"
  issuer              = var.aks_oidc_issuer_url
  audience            = ["api://AzureADTokenExchange"]
}
"""
    
    def _generate_key_vault_terraform(self) -> str:
        """Generate Key Vault specific Terraform configuration"""
        return """
# Key Vault secrets
resource "azurerm_key_vault_secret" "database_password" {
  name         = "database-password"
  value        = random_password.database_password.result
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.terraform_keyvault_admin]
}

resource "azurerm_key_vault_secret" "api_key" {
  name         = "api-key"
  value        = random_uuid.api_key.result
  key_vault_id = azurerm_key_vault.main.id
  
  depends_on = [azurerm_role_assignment.terraform_keyvault_admin]
}

# Random values for secrets
resource "random_password" "database_password" {
  length  = 32
  special = true
}

resource "random_uuid" "api_key" {}

# Role assignment for Terraform to manage Key Vault
resource "azurerm_role_assignment" "terraform_keyvault_admin" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.current.object_id
}

data "azurerm_client_config" "current" {}
"""
    
    def _generate_policy_terraform(self) -> str:
        """Generate Azure Policy Terraform configuration"""
        return """
# Azure Policy for AKS security
resource "azurerm_policy_definition" "aks_network_policy" {
  name         = "aks-require-network-policy"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "AKS clusters should have network policy enabled"
  description  = "Network policy should be enabled on AKS clusters to secure network traffic"

  policy_rule = jsonencode({
    if = {
      allOf = [
        {
          field  = "type"
          equals = "Microsoft.ContainerService/managedClusters"
        },
        {
          anyOf = [
            {
              field  = "Microsoft.ContainerService/managedClusters/networkProfile.networkPolicy"
              exists = "false"
            },
            {
              field     = "Microsoft.ContainerService/managedClusters/networkProfile.networkPolicy"
              notEquals = "calico"
            }
          ]
        }
      ]
    }
    then = {
      effect = "deny"
    }
  })
}

# Policy assignment
resource "azurerm_policy_assignment" "aks_network_policy" {
  name                 = "aks-network-policy-assignment"
  scope                = "/subscriptions/${var.subscription_id}"
  policy_definition_id = azurerm_policy_definition.aks_network_policy.id
  display_name         = "Enforce AKS Network Policy"
  description          = "This assignment enforces that AKS clusters have network policy enabled"
}
"""
    
    def _generate_security_center_terraform(self) -> str:
        """Generate Azure Security Center Terraform configuration"""
        return """
# Security Center subscription pricing
resource "azurerm_security_center_subscription_pricing" "containers" {
  tier          = "Standard"
  resource_type = "Containers"
}

resource "azurerm_security_center_subscription_pricing" "kubernetes" {
  tier          = "Standard"
  resource_type = "Kubernetes"
}

# Security Center contact
resource "azurerm_security_center_contact" "main" {
  email               = var.security_contact_email
  phone               = var.security_contact_phone
  alert_notifications = true
  alerts_to_admins    = true
}

# Auto provisioning
resource "azurerm_security_center_auto_provisioning" "main" {
  auto_provision = "On"
}
"""

    def execute_security_implementation(self) -> Dict[str, Any]:
        """Execute the complete security implementation"""
        security_config = {
            "zero_trust": self.implement_zero_trust_networking(),
            "secret_management": self.implement_secret_management(),
            "compliance": self.implement_compliance_governance(),
            "identity_access": self.implement_identity_access_management(),
            "monitoring": self.implement_security_monitoring(),
            "terraform_templates": self.generate_security_terraform_templates()
        }
        
        return security_config


def main():
    """Main execution function for testing"""
    agent = SecurityAgent(
        subscription_id="your-subscription-id",
        resource_group="rg-aks-demo",
        location="eastus"
    )
    
    security_config = agent.execute_security_implementation()
    
    # Save configurations to files
    with open("zero_trust_config.yaml", "w") as f:
        yaml.dump(security_config["zero_trust"], f, default_flow_style=False)
    
    with open("secret_management_config.yaml", "w") as f:
        yaml.dump(security_config["secret_management"], f, default_flow_style=False)
    
    print("Security implementation completed successfully!")
    print("Generated configurations for:")
    print("- Zero-trust networking and microsegmentation")
    print("- Azure Key Vault integration and secret management")
    print("- Compliance and governance policies")
    print("- Identity and access management")
    print("- Security monitoring and threat detection")


if __name__ == "__main__":
    main()