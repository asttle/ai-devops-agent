#!/usr/bin/env python3
"""
Azure Resource Manager - Core resource creation and management
Handles actual Azure resource provisioning using the Azure SDK
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.storage import StorageManagementClient

from config import get_config

logger = logging.getLogger(__name__)

class AzureResourceManager:
    """
    Azure Resource Manager for creating and managing Azure resources
    Integrates with all specialized agents to provision infrastructure
    """
    
    def __init__(self):
        self.config = get_config()
        self.credential = self.config.azure.get_credential()
        self.subscription_id = self.config.azure.subscription_id
        
        # Initialize Azure clients
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        self.container_client = ContainerServiceClient(self.credential, self.subscription_id)
        self.network_client = NetworkManagementClient(self.credential, self.subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.keyvault_client = KeyVaultManagementClient(self.credential, self.subscription_id)
        self.monitor_client = MonitorManagementClient(self.credential, self.subscription_id)
        self.log_analytics_client = LogAnalyticsManagementClient(self.credential, self.subscription_id)
        self.app_insights_client = ApplicationInsightsManagementClient(self.credential, self.subscription_id)
        self.acr_client = ContainerRegistryManagementClient(self.credential, self.subscription_id)
        self.storage_client = StorageManagementClient(self.credential, self.subscription_id)
        
        logger.info(f"Azure Resource Manager initialized for subscription: {self.subscription_id}")
    
    async def create_resource_group(self, name: str, location: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a new resource group"""
        try:
            logger.info(f"Creating resource group: {name} in {location}")
            
            resource_group_params = {
                'location': location,
                'tags': tags or self.config.get_resource_tags()
            }
            
            result = self.resource_client.resource_groups.create_or_update(
                name, resource_group_params
            )
            
            logger.info(f"Resource group {name} created successfully")
            return {
                'status': 'success',
                'resource_group': {
                    'name': result.name,
                    'location': result.location,
                    'id': result.id,
                    'tags': result.tags,
                    'provisioning_state': result.properties.provisioning_state if result.properties else 'Unknown'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create resource group {name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'resource_group': name
            }
    
    async def create_log_analytics_workspace(self, workspace_name: str, resource_group_name: str, 
                                           location: str, retention_days: int = 30) -> Dict[str, Any]:
        """Create Log Analytics Workspace"""
        try:
            logger.info(f"Creating Log Analytics workspace: {workspace_name}")
            
            workspace_params = {
                'location': location,
                'sku': {'name': 'PerGB2018'},
                'retention_in_days': retention_days,
                'tags': self.config.get_resource_tags({
                    'Service': 'LogAnalytics',
                    'Purpose': 'AKS-Monitoring'
                })
            }
            
            # Check if workspace already exists
            try:
                existing_workspace = self.log_analytics_client.workspaces.get(
                    resource_group_name, workspace_name
                )
                logger.info(f"Log Analytics workspace {workspace_name} already exists")
                return {
                    'status': 'exists',
                    'workspace': {
                        'name': existing_workspace.name,
                        'id': existing_workspace.id,
                        'location': existing_workspace.location,
                        'customer_id': existing_workspace.customer_id,
                        'provisioning_state': existing_workspace.provisioning_state
                    }
                }
            except:
                # Workspace doesn't exist, create it
                pass
            
            # Create the workspace
            operation = self.log_analytics_client.workspaces.begin_create_or_update(
                resource_group_name, workspace_name, workspace_params
            )
            
            # Wait for completion
            result = operation.result()
            
            logger.info(f"Log Analytics workspace {workspace_name} created successfully")
            return {
                'status': 'success',
                'workspace': {
                    'name': result.name,
                    'id': result.id,
                    'location': result.location,
                    'customer_id': result.customer_id,
                    'provisioning_state': result.provisioning_state,
                    'sku': result.sku.name if result.sku else None,
                    'retention_days': result.retention_in_days
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create Log Analytics workspace {workspace_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'workspace_name': workspace_name
            }
    
    async def create_application_insights(self, app_insights_name: str, resource_group_name: str,
                                        location: str, workspace_id: str) -> Dict[str, Any]:
        """Create Application Insights instance"""
        try:
            logger.info(f"Creating Application Insights: {app_insights_name}")
            
            app_insights_params = {
                'location': location,
                'application_type': 'web',
                'workspace_resource_id': workspace_id,
                'retention_in_days': 90,
                'tags': self.config.get_resource_tags({
                    'Service': 'ApplicationInsights',
                    'Purpose': 'AKS-APM'
                })
            }
            
            # Check if Application Insights already exists
            try:
                existing_ai = self.app_insights_client.components.get(
                    resource_group_name, app_insights_name
                )
                logger.info(f"Application Insights {app_insights_name} already exists")
                return {
                    'status': 'exists',
                    'app_insights': {
                        'name': existing_ai.name,
                        'id': existing_ai.id,
                        'location': existing_ai.location,
                        'app_id': existing_ai.app_id,
                        'instrumentation_key': existing_ai.instrumentation_key,
                        'connection_string': existing_ai.connection_string
                    }
                }
            except:
                # Application Insights doesn't exist, create it
                pass
            
            # Create Application Insights
            result = self.app_insights_client.components.create_or_update(
                resource_group_name, app_insights_name, app_insights_params
            )
            
            logger.info(f"Application Insights {app_insights_name} created successfully")
            return {
                'status': 'success',
                'app_insights': {
                    'name': result.name,
                    'id': result.id,
                    'location': result.location,
                    'app_id': result.app_id,
                    'instrumentation_key': result.instrumentation_key,
                    'connection_string': result.connection_string,
                    'provisioning_state': result.provisioning_state,
                    'retention_days': result.retention_in_days
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create Application Insights {app_insights_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'app_insights_name': app_insights_name
            }
    
    async def create_virtual_network(self, vnet_name: str, resource_group_name: str,
                                   location: str, address_space: str = "10.0.0.0/8") -> Dict[str, Any]:
        """Create Virtual Network with subnets"""
        try:
            logger.info(f"Creating Virtual Network: {vnet_name}")
            
            vnet_params = {
                'location': location,
                'address_space': {
                    'address_prefixes': [address_space]
                },
                'subnets': [
                    {
                        'name': 'aks-subnet',
                        'address_prefix': '10.1.0.0/16',
                        'private_endpoint_network_policies': 'Disabled'
                    },
                    {
                        'name': 'appgw-subnet',
                        'address_prefix': '10.2.0.0/24'
                    },
                    {
                        'name': 'private-endpoints-subnet',
                        'address_prefix': '10.3.0.0/24',
                        'private_endpoint_network_policies': 'Enabled'
                    }
                ],
                'tags': self.config.get_resource_tags({
                    'Service': 'Network',
                    'Purpose': 'AKS-Infrastructure'
                })
            }
            
            # Check if VNet already exists
            try:
                existing_vnet = self.network_client.virtual_networks.get(
                    resource_group_name, vnet_name
                )
                logger.info(f"Virtual Network {vnet_name} already exists")
                return {
                    'status': 'exists',
                    'vnet': {
                        'name': existing_vnet.name,
                        'id': existing_vnet.id,
                        'location': existing_vnet.location,
                        'address_space': existing_vnet.address_space.address_prefixes,
                        'subnets': [
                            {
                                'name': subnet.name,
                                'id': subnet.id,
                                'address_prefix': subnet.address_prefix
                            }
                            for subnet in existing_vnet.subnets
                        ]
                    }
                }
            except:
                # VNet doesn't exist, create it
                pass
            
            # Create Virtual Network
            operation = self.network_client.virtual_networks.begin_create_or_update(
                resource_group_name, vnet_name, vnet_params
            )
            
            # Wait for completion
            result = operation.result()
            
            logger.info(f"Virtual Network {vnet_name} created successfully")
            return {
                'status': 'success',
                'vnet': {
                    'name': result.name,
                    'id': result.id,
                    'location': result.location,
                    'address_space': result.address_space.address_prefixes,
                    'provisioning_state': result.provisioning_state,
                    'subnets': [
                        {
                            'name': subnet.name,
                            'id': subnet.id,
                            'address_prefix': subnet.address_prefix,
                            'provisioning_state': subnet.provisioning_state
                        }
                        for subnet in result.subnets
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create Virtual Network {vnet_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'vnet_name': vnet_name
            }
    
    async def create_aks_cluster(self, cluster_name: str, resource_group_name: str,
                               location: str, node_count: int = 3, vm_size: str = "Standard_B2s",
                               kubernetes_version: str = "1.28", subnet_id: Optional[str] = None,
                               log_analytics_workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """Create AKS Cluster with best practices"""
        try:
            logger.info(f"Creating AKS cluster: {cluster_name}")
            
            # Base AKS configuration
            aks_params = {
                'location': location,
                'dns_prefix': cluster_name,
                'kubernetes_version': kubernetes_version,
                'enable_rbac': True,
                'network_profile': {
                    'network_plugin': 'azure',
                    'network_policy': 'calico',
                    'service_cidr': '10.0.0.0/16',
                    'dns_service_ip': '10.0.0.10',
                    'load_balancer_sku': 'standard'
                },
                'api_server_access_profile': {
                    'enable_private_cluster': True
                },
                'identity': {
                    'type': 'SystemAssigned'
                },
                'addon_profiles': {},
                'agent_pool_profiles': [
                    {
                        'name': 'default',
                        'count': node_count,
                        'vm_size': vm_size,
                        'type': 'VirtualMachineScaleSets',
                        'mode': 'System',
                        'os_type': 'Linux',
                        'enable_auto_scaling': True,
                        'min_count': 1,
                        'max_count': 10,
                        'vnet_subnet_id': subnet_id
                    }
                ],
                'tags': self.config.get_resource_tags({
                    'Service': 'AKS',
                    'Purpose': 'Kubernetes-Cluster'
                })
            }
            
            # Add Log Analytics integration if workspace provided
            if log_analytics_workspace_id:
                aks_params['addon_profiles']['omsAgent'] = {
                    'enabled': True,
                    'config': {
                        'logAnalyticsWorkspaceResourceID': log_analytics_workspace_id
                    }
                }
                aks_params['addon_profiles']['azurepolicy'] = {'enabled': True}
            
            # Check if AKS cluster already exists
            try:
                existing_cluster = self.container_client.managed_clusters.get(
                    resource_group_name, cluster_name
                )
                logger.info(f"AKS cluster {cluster_name} already exists")
                return {
                    'status': 'exists',
                    'cluster': {
                        'name': existing_cluster.name,
                        'id': existing_cluster.id,
                        'location': existing_cluster.location,
                        'fqdn': existing_cluster.fqdn,
                        'kubernetes_version': existing_cluster.kubernetes_version,
                        'provisioning_state': existing_cluster.provisioning_state,
                        'node_resource_group': existing_cluster.node_resource_group,
                        'agent_pools': [
                            {
                                'name': pool.name,
                                'count': pool.count,
                                'vm_size': pool.vm_size,
                                'provisioning_state': pool.provisioning_state
                            }
                            for pool in existing_cluster.agent_pool_profiles
                        ]
                    }
                }
            except:
                # Cluster doesn't exist, create it
                pass
            
            # Create AKS cluster
            logger.info(f"Starting AKS cluster creation for {cluster_name} (this may take 10-15 minutes)")
            operation = self.container_client.managed_clusters.begin_create_or_update(
                resource_group_name, cluster_name, aks_params
            )
            
            # Wait for completion
            result = operation.result()
            
            logger.info(f"AKS cluster {cluster_name} created successfully")
            return {
                'status': 'success',
                'cluster': {
                    'name': result.name,
                    'id': result.id,
                    'location': result.location,
                    'fqdn': result.fqdn,
                    'kubernetes_version': result.kubernetes_version,
                    'provisioning_state': result.provisioning_state,
                    'node_resource_group': result.node_resource_group,
                    'identity': {
                        'type': result.identity.type if result.identity else None,
                        'principal_id': result.identity.principal_id if result.identity else None
                    },
                    'agent_pools': [
                        {
                            'name': pool.name,
                            'count': pool.count,
                            'vm_size': pool.vm_size,
                            'provisioning_state': pool.provisioning_state,
                            'auto_scaling_enabled': pool.enable_auto_scaling,
                            'min_count': pool.min_count,
                            'max_count': pool.max_count
                        }
                        for pool in result.agent_pool_profiles
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create AKS cluster {cluster_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'cluster_name': cluster_name
            }
    
    async def create_container_registry(self, acr_name: str, resource_group_name: str,
                                      location: str, sku: str = "Premium") -> Dict[str, Any]:
        """Create Azure Container Registry"""
        try:
            logger.info(f"Creating Container Registry: {acr_name}")
            
            acr_params = {
                'location': location,
                'sku': {'name': sku},
                'admin_user_enabled': False,
                'network_rule_set': {
                    'default_action': 'Deny'
                },
                'public_network_access': 'Disabled',
                'tags': self.config.get_resource_tags({
                    'Service': 'ContainerRegistry',
                    'Purpose': 'Container-Images'
                })
            }
            
            # Check if ACR already exists
            try:
                existing_acr = self.acr_client.registries.get(resource_group_name, acr_name)
                logger.info(f"Container Registry {acr_name} already exists")
                return {
                    'status': 'exists',
                    'registry': {
                        'name': existing_acr.name,
                        'id': existing_acr.id,
                        'location': existing_acr.location,
                        'login_server': existing_acr.login_server,
                        'provisioning_state': existing_acr.provisioning_state,
                        'sku': existing_acr.sku.name if existing_acr.sku else None
                    }
                }
            except:
                # ACR doesn't exist, create it
                pass
            
            # Create Container Registry
            operation = self.acr_client.registries.begin_create(
                resource_group_name, acr_name, acr_params
            )
            
            # Wait for completion
            result = operation.result()
            
            logger.info(f"Container Registry {acr_name} created successfully")
            return {
                'status': 'success',
                'registry': {
                    'name': result.name,
                    'id': result.id,
                    'location': result.location,
                    'login_server': result.login_server,
                    'provisioning_state': result.provisioning_state,
                    'sku': result.sku.name if result.sku else None,
                    'admin_user_enabled': result.admin_user_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create Container Registry {acr_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'registry_name': acr_name
            }
    
    async def create_key_vault(self, vault_name: str, resource_group_name: str,
                             location: str, tenant_id: str) -> Dict[str, Any]:
        """Create Azure Key Vault"""
        try:
            logger.info(f"Creating Key Vault: {vault_name}")
            
            vault_params = {
                'location': location,
                'properties': {
                    'tenant_id': tenant_id,
                    'sku': {'name': 'premium', 'family': 'A'},
                    'enabled_for_disk_encryption': True,
                    'enabled_for_template_deployment': True,
                    'enabled_for_deployment': True,
                    'enable_rbac_authorization': True,
                    'enable_purge_protection': True,
                    'enable_soft_delete': True,
                    'soft_delete_retention_in_days': 90,
                    'network_acls': {
                        'default_action': 'Deny',
                        'bypass': 'AzureServices'
                    }
                },
                'tags': self.config.get_resource_tags({
                    'Service': 'KeyVault',
                    'Purpose': 'Secrets-Management'
                })
            }
            
            # Check if Key Vault already exists
            try:
                existing_vault = self.keyvault_client.vaults.get(resource_group_name, vault_name)
                logger.info(f"Key Vault {vault_name} already exists")
                return {
                    'status': 'exists',
                    'vault': {
                        'name': existing_vault.name,
                        'id': existing_vault.id,
                        'location': existing_vault.location,
                        'vault_uri': existing_vault.properties.vault_uri if existing_vault.properties else None,
                        'tenant_id': existing_vault.properties.tenant_id if existing_vault.properties else None
                    }
                }
            except:
                # Key Vault doesn't exist, create it
                pass
            
            # Create Key Vault
            operation = self.keyvault_client.vaults.begin_create_or_update(
                resource_group_name, vault_name, vault_params
            )
            
            # Wait for completion
            result = operation.result()
            
            logger.info(f"Key Vault {vault_name} created successfully")
            return {
                'status': 'success',
                'vault': {
                    'name': result.name,
                    'id': result.id,
                    'location': result.location,
                    'vault_uri': result.properties.vault_uri if result.properties else None,
                    'tenant_id': result.properties.tenant_id if result.properties else None,
                    'sku': result.properties.sku.name if result.properties and result.properties.sku else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create Key Vault {vault_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'vault_name': vault_name
            }
    
    async def get_resource_status(self, resource_type: str, resource_name: str, 
                                resource_group_name: str) -> Dict[str, Any]:
        """Get status of a specific resource"""
        try:
            if resource_type.lower() == 'aks' or resource_type.lower() == 'cluster':
                resource = self.container_client.managed_clusters.get(resource_group_name, resource_name)
                return {
                    'name': resource.name,
                    'type': 'AKS Cluster',
                    'status': resource.provisioning_state,
                    'location': resource.location,
                    'kubernetes_version': resource.kubernetes_version
                }
            elif resource_type.lower() == 'loganalytics' or resource_type.lower() == 'workspace':
                resource = self.log_analytics_client.workspaces.get(resource_group_name, resource_name)
                return {
                    'name': resource.name,
                    'type': 'Log Analytics Workspace',
                    'status': resource.provisioning_state,
                    'location': resource.location,
                    'customer_id': resource.customer_id
                }
            elif resource_type.lower() == 'applicationinsights' or resource_type.lower() == 'appinsights':
                resource = self.app_insights_client.components.get(resource_group_name, resource_name)
                return {
                    'name': resource.name,
                    'type': 'Application Insights',
                    'status': resource.provisioning_state,
                    'location': resource.location,
                    'app_id': resource.app_id
                }
            else:
                return {
                    'error': f'Unsupported resource type: {resource_type}'
                }
                
        except Exception as e:
            return {
                'error': f'Resource not found or error occurred: {str(e)}'
            }
    
    async def list_resources_in_group(self, resource_group_name: str) -> List[Dict[str, Any]]:
        """List all resources in a resource group"""
        try:
            resources = []
            resource_list = self.resource_client.resources.list_by_resource_group(resource_group_name)
            
            for resource in resource_list:
                resources.append({
                    'name': resource.name,
                    'type': resource.type,
                    'location': resource.location,
                    'id': resource.id,
                    'tags': resource.tags or {}
                })
            
            return resources
            
        except Exception as e:
            logger.error(f"Failed to list resources in {resource_group_name}: {str(e)}")
            return []
    
    async def cleanup_resource_group(self, resource_group_name: str) -> Dict[str, Any]:
        """Delete a resource group and all its resources"""
        try:
            logger.warning(f"Deleting resource group: {resource_group_name}")
            
            operation = self.resource_client.resource_groups.begin_delete(resource_group_name)
            operation.wait()
            
            logger.info(f"Resource group {resource_group_name} deleted successfully")
            return {
                'status': 'success',
                'message': f'Resource group {resource_group_name} and all resources deleted'
            }
            
        except Exception as e:
            logger.error(f"Failed to delete resource group {resource_group_name}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

# Global instance
azure_manager = AzureResourceManager()

def get_azure_manager() -> AzureResourceManager:
    """Get the global Azure Resource Manager instance"""
    return azure_manager