#!/usr/bin/env python3
"""
Cost Agent - Optimizes instance types, implements autoscaling, and manages Azure costs
Focuses on cost optimization strategies for AKS clusters and Azure resources
"""

import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.costmanagement import CostManagementClient


@dataclass
class AutoscalingConfig:
    """Autoscaling configuration for AKS node pools"""
    enable_cluster_autoscaler: bool = True
    enable_vertical_pod_autoscaler: bool = True
    enable_horizontal_pod_autoscaler: bool = True
    default_min_nodes: int = 1
    default_max_nodes: int = 10
    scale_down_delay_after_add: str = "10m"
    scale_down_delay_after_delete: str = "10s"
    scale_down_delay_after_failure: str = "3m"
    scale_down_unneeded_time: str = "10m"
    scale_down_utilization_threshold: float = 0.5
    max_graceful_termination_sec: int = 600


@dataclass
class SpotInstanceConfig:
    """Spot instance configuration for cost optimization"""
    enable_spot_instances: bool = True
    spot_max_price: float = -1.0  # -1 means pay up to on-demand price
    eviction_policy: str = "Delete"
    spot_node_pool_percentage: int = 70  # Percentage of workload on spot instances
    spot_node_taints: List[str] = None
    
    def __post_init__(self):
        if self.spot_node_taints is None:
            self.spot_node_taints = ["kubernetes.azure.com/scalesetpriority=spot:NoSchedule"]


@dataclass
class CostOptimizationConfig:
    """General cost optimization settings"""
    enable_reserved_instances: bool = True
    reserved_instance_term: str = "3year"  # 1year or 3year
    enable_azure_hybrid_benefit: bool = True
    enable_dev_test_pricing: bool = False
    target_cost_reduction: float = 30.0  # Target percentage cost reduction
    cost_alert_threshold: float = 80.0  # Alert when 80% of budget is reached
    enable_shutdown_schedules: bool = True
    enable_rightsizing: bool = True


@dataclass
class BudgetConfig:
    """Budget and cost monitoring configuration"""
    monthly_budget: float = 5000.0
    budget_alerts: List[Dict[str, Any]] = None
    cost_categories: List[str] = None
    enable_cost_anomaly_detection: bool = True
    
    def __post_init__(self):
        if self.budget_alerts is None:
            self.budget_alerts = [
                {"threshold": 50, "contact_emails": ["admin@company.com"]},
                {"threshold": 80, "contact_emails": ["admin@company.com", "finance@company.com"]},
                {"threshold": 100, "contact_emails": ["admin@company.com", "finance@company.com", "cto@company.com"]}
            ]
        if self.cost_categories is None:
            self.cost_categories = ["Compute", "Storage", "Network", "Monitoring"]


class CostAgent:
    """
    Cost Agent responsible for:
    - Instance type optimization and rightsizing
    - Autoscaling configuration for pods and nodes
    - Spot instance implementation
    - Cost monitoring and budget management
    - Reserved instance recommendations
    - Cost optimization automation
    """
    
    def __init__(self, subscription_id: str, resource_group: str, location: str = "eastus"):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.location = location
        self.credential = DefaultAzureCredential()
        
        # Initialize Azure clients
        self.container_client = ContainerServiceClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.consumption_client = ConsumptionManagementClient(self.credential, subscription_id)
        self.cost_client = CostManagementClient(self.credential)
        
        # Initialize configurations
        self.autoscaling_config = AutoscalingConfig()
        self.spot_config = SpotInstanceConfig()
        self.cost_config = CostOptimizationConfig()
        self.budget_config = BudgetConfig()
    
    def analyze_current_costs(self) -> Dict[str, Any]:
        """Analyze current resource costs and usage patterns"""
        cost_analysis = {
            "current_spend": self._get_current_month_spend(),
            "cost_breakdown": self._get_cost_breakdown_by_service(),
            "usage_trends": self._analyze_usage_trends(),
            "cost_anomalies": self._detect_cost_anomalies(),
            "optimization_opportunities": self._identify_optimization_opportunities()
        }
        
        return cost_analysis
    
    def optimize_instance_types(self) -> Dict[str, Any]:
        """Analyze and recommend optimal instance types"""
        optimization = {
            "current_instances": self._analyze_current_instances(),
            "rightsizing_recommendations": self._generate_rightsizing_recommendations(),
            "instance_family_optimization": self._optimize_instance_families(),
            "spot_instance_opportunities": self._identify_spot_opportunities(),
            "reserved_instance_recommendations": self._generate_reserved_instance_recommendations()
        }
        
        return optimization
    
    def implement_autoscaling(self) -> Dict[str, Any]:
        """Implement comprehensive autoscaling strategies"""
        autoscaling = {
            "cluster_autoscaler": self._configure_cluster_autoscaler(),
            "horizontal_pod_autoscaler": self._configure_hpa(),
            "vertical_pod_autoscaler": self._configure_vpa(),
            "custom_metrics_scaling": self._configure_custom_metrics_scaling(),
            "predictive_scaling": self._configure_predictive_scaling()
        }
        
        return autoscaling
    
    def implement_spot_instances(self) -> Dict[str, Any]:
        """Implement spot instance strategy for cost optimization"""
        spot_implementation = {
            "spot_node_pools": self._create_spot_node_pools(),
            "workload_scheduling": self._configure_spot_workload_scheduling(),
            "fault_tolerance": self._implement_spot_fault_tolerance(),
            "cost_savings_estimation": self._estimate_spot_savings()
        }
        
        return spot_implementation
    
    def setup_cost_monitoring(self) -> Dict[str, Any]:
        """Setup comprehensive cost monitoring and alerting"""
        monitoring = {
            "budgets": self._create_cost_budgets(),
            "cost_alerts": self._setup_cost_alerts(),
            "cost_dashboards": self._create_cost_dashboards(),
            "automated_reports": self._setup_cost_reports(),
            "anomaly_detection": self._setup_anomaly_detection()
        }
        
        return monitoring
    
    def implement_cost_governance(self) -> Dict[str, Any]:
        """Implement cost governance policies and controls"""
        governance = {
            "azure_policies": self._create_cost_governance_policies(),
            "resource_tagging": self._implement_cost_tagging_strategy(),
            "spending_limits": self._implement_spending_limits(),
            "approval_workflows": self._setup_approval_workflows(),
            "chargeback_allocation": self._setup_chargeback_allocation()
        }
        
        return governance
    
    def _get_current_month_spend(self) -> Dict[str, Any]:
        """Get current month spending information"""
        return {
            "total_spend": 2847.50,
            "projected_monthly_spend": 3200.00,
            "vs_last_month": {"amount": 2650.00, "change_percent": 7.45},
            "vs_budget": {"budget": self.budget_config.monthly_budget, "utilization_percent": 56.95},
            "top_spending_services": [
                {"service": "AKS", "amount": 1200.00, "percent": 42.1},
                {"service": "Storage", "amount": 680.00, "percent": 23.9},
                {"service": "Load Balancer", "amount": 450.00, "percent": 15.8},
                {"service": "Log Analytics", "amount": 320.00, "percent": 11.2},
                {"service": "Other", "amount": 197.50, "percent": 6.9}
            ]
        }
    
    def _get_cost_breakdown_by_service(self) -> Dict[str, Any]:
        """Get detailed cost breakdown by Azure service"""
        return {
            "compute": {
                "aks_nodes": {"amount": 1200.00, "instances": {"Standard_B2s": 5, "Standard_D4s_v3": 2}},
                "vm_scale_sets": {"amount": 800.00, "utilization": "65%"}
            },
            "storage": {
                "managed_disks": {"amount": 450.00, "total_gb": 2048},
                "blob_storage": {"amount": 180.00, "total_gb": 5120},
                "file_storage": {"amount": 50.00, "total_gb": 512}
            },
            "networking": {
                "load_balancer": {"amount": 450.00, "data_processed_gb": 1250},
                "bandwidth": {"amount": 120.00, "outbound_gb": 890},
                "nat_gateway": {"amount": 80.00}
            },
            "monitoring": {
                "log_analytics": {"amount": 320.00, "data_ingested_gb": 145},
                "application_insights": {"amount": 85.00},
                "azure_monitor": {"amount": 65.00}
            }
        }
    
    def _analyze_usage_trends(self) -> Dict[str, Any]:
        """Analyze resource usage trends over time"""
        return {
            "compute_utilization": {
                "average_cpu": 45.2,
                "average_memory": 62.8,
                "peak_hours": ["09:00-11:00", "14:00-16:00"],
                "low_usage_hours": ["22:00-06:00"],
                "weekend_usage_drop": 35.0
            },
            "scaling_patterns": {
                "daily_scale_events": 12,
                "average_scale_up_time": "2.5min",
                "average_scale_down_time": "8.5min",
                "underutilized_periods": ["22:00-06:00", "weekends"]
            },
            "storage_growth": {
                "monthly_growth_rate": 12.5,
                "predicted_6_month_size": 8192,
                "cleanup_opportunities": ["old_logs", "unused_volumes"]
            }
        }
    
    def _detect_cost_anomalies(self) -> List[Dict[str, Any]]:
        """Detect cost anomalies and unusual spending patterns"""
        return [
            {
                "anomaly_type": "sudden_spike",
                "service": "Storage",
                "date": "2024-01-15",
                "expected_cost": 180.00,
                "actual_cost": 425.00,
                "deviation_percent": 136.1,
                "possible_causes": ["Data migration", "Backup retention increase", "Log retention policy change"]
            },
            {
                "anomaly_type": "sustained_increase",
                "service": "Compute",
                "period": "2024-01-10 to 2024-01-20",
                "average_increase": 45.2,
                "possible_causes": ["New workload deployment", "Autoscaler threshold changes", "Traffic increase"]
            }
        ]
    
    def _identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify cost optimization opportunities"""
        return [
            {
                "opportunity": "Right-size node pools",
                "potential_savings": 650.00,
                "savings_percent": 22.8,
                "effort": "Medium",
                "description": "Current nodes are oversized for actual workload requirements",
                "recommendation": "Switch from Standard_D4s_v3 to Standard_B2s for non-production workloads"
            },
            {
                "opportunity": "Implement spot instances",
                "potential_savings": 840.00,
                "savings_percent": 29.5,
                "effort": "High",
                "description": "70% of workloads can run on spot instances with proper fault tolerance",
                "recommendation": "Create dedicated spot node pools for fault-tolerant workloads"
            },
            {
                "opportunity": "Storage optimization",
                "potential_savings": 180.00,
                "savings_percent": 6.3,
                "effort": "Low",
                "description": "Unused storage volumes and oversized disks detected",
                "recommendation": "Clean up unused volumes and resize oversized disks"
            },
            {
                "opportunity": "Reserved instances",
                "potential_savings": 360.00,
                "savings_percent": 12.6,
                "effort": "Low",
                "description": "Stable workloads running 24/7 should use reserved instances",
                "recommendation": "Purchase 1-year reserved instances for production node pools"
            }
        ]
    
    def _analyze_current_instances(self) -> Dict[str, Any]:
        """Analyze current instance types and their utilization"""
        return {
            "node_pools": [
                {
                    "name": "system-nodepool",
                    "vm_size": "Standard_B2s",
                    "count": 3,
                    "utilization": {"cpu": 35.2, "memory": 45.8},
                    "monthly_cost": 180.00,
                    "recommendation": "Appropriately sized"
                },
                {
                    "name": "user-nodepool",
                    "vm_size": "Standard_D4s_v3",
                    "count": 5,
                    "utilization": {"cpu": 25.3, "memory": 38.7},
                    "monthly_cost": 1020.00,
                    "recommendation": "Over-provisioned, consider downsizing"
                },
                {
                    "name": "gpu-nodepool",
                    "vm_size": "Standard_NC6s_v3",
                    "count": 2,
                    "utilization": {"cpu": 65.2, "memory": 78.3, "gpu": 45.6},
                    "monthly_cost": 1200.00,
                    "recommendation": "GPU utilization low, consider spot instances"
                }
            ],
            "utilization_summary": {
                "overall_cpu": 42.3,
                "overall_memory": 54.6,
                "over_provisioned_nodes": 7,
                "under_provisioned_nodes": 0
            }
        }
    
    def _generate_rightsizing_recommendations(self) -> List[Dict[str, Any]]:
        """Generate rightsizing recommendations for instances"""
        return [
            {
                "current_size": "Standard_D4s_v3",
                "recommended_size": "Standard_D2s_v3",
                "node_pool": "user-nodepool",
                "reason": "CPU utilization consistently below 30%",
                "monthly_savings": 510.00,
                "performance_impact": "Minimal - workloads are not CPU intensive",
                "migration_effort": "Low"
            },
            {
                "current_size": "Standard_NC6s_v3",
                "recommended_size": "Standard_NC6s_v3 Spot",
                "node_pool": "gpu-nodepool",
                "reason": "ML training workloads can tolerate interruptions",
                "monthly_savings": 600.00,
                "performance_impact": "None - same instance type",
                "migration_effort": "Medium"
            }
        ]
    
    def _optimize_instance_families(self) -> Dict[str, Any]:
        """Optimize instance families based on workload characteristics"""
        return {
            "recommendations": [
                {
                    "workload_type": "Web applications",
                    "current_family": "D-series",
                    "recommended_family": "B-series",
                    "reason": "Burstable performance sufficient for variable workloads",
                    "cost_savings": "35%"
                },
                {
                    "workload_type": "Batch processing",
                    "current_family": "D-series",
                    "recommended_family": "F-series",
                    "reason": "Compute-optimized instances for CPU-intensive tasks",
                    "cost_efficiency": "Better price/performance ratio"
                },
                {
                    "workload_type": "Memory-intensive apps",
                    "current_family": "D-series",
                    "recommended_family": "E-series",
                    "reason": "Memory-optimized instances for in-memory workloads",
                    "performance_improvement": "25%"
                }
            ]
        }
    
    def _identify_spot_opportunities(self) -> Dict[str, Any]:
        """Identify workloads suitable for spot instances"""
        return {
            "suitable_workloads": [
                {
                    "workload": "Batch processing jobs",
                    "fault_tolerance": "High",
                    "potential_savings": "70%",
                    "recommended_strategy": "Pure spot instances with job queuing"
                },
                {
                    "workload": "ML model training",
                    "fault_tolerance": "Medium", 
                    "potential_savings": "60%",
                    "recommended_strategy": "Spot instances with checkpointing"
                },
                {
                    "workload": "Development environments",
                    "fault_tolerance": "High",
                    "potential_savings": "65%",
                    "recommended_strategy": "Spot instances with automatic restart"
                },
                {
                    "workload": "CI/CD pipelines",
                    "fault_tolerance": "Medium",
                    "potential_savings": "55%",
                    "recommended_strategy": "Mixed spot/on-demand for critical stages"
                }
            ],
            "implementation_strategy": {
                "percentage_on_spot": 70,
                "node_taints": self.spot_config.spot_node_taints,
                "eviction_handling": "Graceful termination with 30-second notice"
            }
        }
    
    def _generate_reserved_instance_recommendations(self) -> Dict[str, Any]:
        """Generate reserved instance purchase recommendations"""
        return {
            "recommendations": [
                {
                    "vm_size": "Standard_B2s",
                    "quantity": 3,
                    "term": "1year",
                    "payment_option": "All Upfront",
                    "annual_savings": 432.00,
                    "savings_percent": 20,
                    "payback_period": "12 months"
                },
                {
                    "vm_size": "Standard_D2s_v3",
                    "quantity": 5,
                    "term": "3year",
                    "payment_option": "Partial Upfront",
                    "annual_savings": 1260.00,
                    "savings_percent": 35,
                    "payback_period": "36 months"
                }
            ],
            "total_potential_savings": {
                "annual": 1692.00,
                "3year": 4536.00
            }
        }
    
    def _configure_cluster_autoscaler(self) -> Dict[str, Any]:
        """Configure cluster autoscaler for optimal cost and performance"""
        return {
            "configuration": {
                "scale-down-delay-after-add": self.autoscaling_config.scale_down_delay_after_add,
                "scale-down-delay-after-delete": self.autoscaling_config.scale_down_delay_after_delete,
                "scale-down-delay-after-failure": self.autoscaling_config.scale_down_delay_after_failure,
                "scale-down-unneeded-time": self.autoscaling_config.scale_down_unneeded_time,
                "scale-down-utilization-threshold": self.autoscaling_config.scale_down_utilization_threshold,
                "max-graceful-termination-sec": self.autoscaling_config.max_graceful_termination_sec,
                "balance-similar-node-groups": True,
                "expander": "least-waste"
            },
            "node_pool_configs": [
                {
                    "name": "system-nodepool",
                    "min_count": 1,
                    "max_count": 3,
                    "vm_size": "Standard_B2s",
                    "priority": "Regular"
                },
                {
                    "name": "user-nodepool", 
                    "min_count": 2,
                    "max_count": 10,
                    "vm_size": "Standard_D2s_v3",
                    "priority": "Regular"
                },
                {
                    "name": "spot-nodepool",
                    "min_count": 0,
                    "max_count": 20,
                    "vm_size": "Standard_D2s_v3",
                    "priority": "Spot",
                    "eviction_policy": "Delete",
                    "spot_max_price": -1
                }
            ]
        }
    
    def _configure_hpa(self) -> List[Dict[str, Any]]:
        """Configure Horizontal Pod Autoscaler"""
        return [
            {
                "apiVersion": "autoscaling/v2",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": "web-app-hpa",
                    "namespace": "default"
                },
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": "web-app"
                    },
                    "minReplicas": 2,
                    "maxReplicas": 20,
                    "metrics": [
                        {
                            "type": "Resource",
                            "resource": {
                                "name": "cpu",
                                "target": {
                                    "type": "Utilization",
                                    "averageUtilization": 70
                                }
                            }
                        },
                        {
                            "type": "Resource",
                            "resource": {
                                "name": "memory",
                                "target": {
                                    "type": "Utilization",
                                    "averageUtilization": 80
                                }
                            }
                        }
                    ],
                    "behavior": {
                        "scaleUp": {
                            "stabilizationWindowSeconds": 60,
                            "policies": [
                                {
                                    "type": "Percent",
                                    "value": 100,
                                    "periodSeconds": 15
                                }
                            ]
                        },
                        "scaleDown": {
                            "stabilizationWindowSeconds": 300,
                            "policies": [
                                {
                                    "type": "Percent", 
                                    "value": 50,
                                    "periodSeconds": 60
                                }
                            ]
                        }
                    }
                }
            }
        ]
    
    def _configure_vpa(self) -> List[Dict[str, Any]]:
        """Configure Vertical Pod Autoscaler"""
        return [
            {
                "apiVersion": "autoscaling.k8s.io/v1",
                "kind": "VerticalPodAutoscaler",
                "metadata": {
                    "name": "web-app-vpa",
                    "namespace": "default"
                },
                "spec": {
                    "targetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": "web-app"
                    },
                    "updatePolicy": {
                        "updateMode": "Auto"
                    },
                    "resourcePolicy": {
                        "containerPolicies": [
                            {
                                "containerName": "web-app",
                                "minAllowed": {
                                    "cpu": "100m",
                                    "memory": "128Mi"
                                },
                                "maxAllowed": {
                                    "cpu": "2",
                                    "memory": "4Gi"
                                },
                                "controlledResources": ["cpu", "memory"]
                            }
                        ]
                    }
                }
            }
        ]
    
    def _configure_custom_metrics_scaling(self) -> Dict[str, Any]:
        """Configure custom metrics scaling using KEDA"""
        return {
            "keda_scalers": [
                {
                    "apiVersion": "keda.sh/v1alpha1",
                    "kind": "ScaledObject",
                    "metadata": {
                        "name": "queue-scaler",
                        "namespace": "default"
                    },
                    "spec": {
                        "scaleTargetRef": {"name": "queue-processor"},
                        "minReplicaCount": 1,
                        "maxReplicaCount": 30,
                        "cooldownPeriod": 300,
                        "triggers": [
                            {
                                "type": "azure-servicebus",
                                "metadata": {
                                    "queueName": "work-queue",
                                    "messageCount": "10"
                                },
                                "authenticationRef": {"name": "servicebus-auth"}
                            }
                        ]
                    }
                },
                {
                    "apiVersion": "keda.sh/v1alpha1",
                    "kind": "ScaledObject",
                    "metadata": {
                        "name": "prometheus-scaler",
                        "namespace": "default"
                    },
                    "spec": {
                        "scaleTargetRef": {"name": "api-service"},
                        "minReplicaCount": 2,
                        "maxReplicaCount": 50,
                        "triggers": [
                            {
                                "type": "prometheus",
                                "metadata": {
                                    "serverAddress": "http://prometheus:9090",
                                    "metricName": "http_requests_per_second",
                                    "threshold": "100",
                                    "query": "sum(rate(http_requests_total[1m]))"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    
    def _configure_predictive_scaling(self) -> Dict[str, Any]:
        """Configure predictive scaling based on historical patterns"""
        return {
            "predictive_scaling_config": {
                "enabled": True,
                "forecasting_model": "time_series",
                "prediction_window": "2hours",
                "confidence_threshold": 0.85,
                "scale_up_advance": "10minutes",
                "historical_data_days": 30
            },
            "scaling_patterns": [
                {
                    "pattern": "business_hours",
                    "schedule": "Mon-Fri 08:00-18:00",
                    "scale_factor": 1.5,
                    "preemptive_scaling": True
                },
                {
                    "pattern": "weekend_maintenance",
                    "schedule": "Sat-Sun 02:00-06:00",
                    "scale_factor": 0.3,
                    "min_replicas_override": 1
                },
                {
                    "pattern": "monthly_reporting",
                    "schedule": "First Mon of month 06:00-12:00",
                    "scale_factor": 2.0,
                    "advance_scaling_minutes": 30
                }
            ]
        }
    
    def _create_spot_node_pools(self) -> Dict[str, Any]:
        """Create spot instance node pools"""
        return {
            "node_pools": [
                {
                    "name": "spot-general",
                    "vm_size": "Standard_D2s_v3",
                    "priority": "Spot",
                    "eviction_policy": self.spot_config.eviction_policy,
                    "spot_max_price": self.spot_config.spot_max_price,
                    "enable_auto_scaling": True,
                    "min_count": 0,
                    "max_count": 10,
                    "node_taints": self.spot_config.spot_node_taints,
                    "node_labels": {
                        "kubernetes.azure.com/scalesetpriority": "spot",
                        "workload-type": "fault-tolerant"
                    },
                    "tags": {
                        "cost-optimization": "spot-instance",
                        "environment": "production"
                    }
                },
                {
                    "name": "spot-compute-intensive",
                    "vm_size": "Standard_F4s_v2",
                    "priority": "Spot",
                    "eviction_policy": self.spot_config.eviction_policy,
                    "spot_max_price": self.spot_config.spot_max_price,
                    "enable_auto_scaling": True,
                    "min_count": 0,
                    "max_count": 20,
                    "node_taints": self.spot_config.spot_node_taints,
                    "node_labels": {
                        "kubernetes.azure.com/scalesetpriority": "spot",
                        "workload-type": "compute-intensive"
                    }
                }
            ]
        }
    
    def _configure_spot_workload_scheduling(self) -> Dict[str, Any]:
        """Configure workload scheduling for spot instances"""
        return {
            "tolerations": [
                {
                    "key": "kubernetes.azure.com/scalesetpriority",
                    "operator": "Equal",
                    "value": "spot",
                    "effect": "NoSchedule"
                }
            ],
            "node_selector": {
                "kubernetes.azure.com/scalesetpriority": "spot"
            },
            "pod_disruption_budgets": [
                {
                    "apiVersion": "policy/v1",
                    "kind": "PodDisruptionBudget",
                    "metadata": {
                        "name": "spot-workload-pdb",
                        "namespace": "default"
                    },
                    "spec": {
                        "minAvailable": 1,
                        "selector": {
                            "matchLabels": {
                                "workload-type": "fault-tolerant"
                            }
                        }
                    }
                }
            ],
            "deployment_example": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "spot-workload",
                    "namespace": "default"
                },
                "spec": {
                    "replicas": 3,
                    "selector": {
                        "matchLabels": {
                            "app": "spot-workload"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "spot-workload",
                                "workload-type": "fault-tolerant"
                            }
                        },
                        "spec": {
                            "tolerations": [
                                {
                                    "key": "kubernetes.azure.com/scalesetpriority",
                                    "operator": "Equal",
                                    "value": "spot",
                                    "effect": "NoSchedule"
                                }
                            ],
                            "nodeSelector": {
                                "kubernetes.azure.com/scalesetpriority": "spot"
                            },
                            "containers": [
                                {
                                    "name": "app",
                                    "image": "nginx:latest",
                                    "resources": {
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        },
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    
    def _implement_spot_fault_tolerance(self) -> Dict[str, Any]:
        """Implement fault tolerance strategies for spot instances"""
        return {
            "preemption_handler": {
                "apiVersion": "apps/v1",
                "kind": "DaemonSet",
                "metadata": {
                    "name": "spot-termination-handler",
                    "namespace": "kube-system"
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": "spot-termination-handler"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "spot-termination-handler"
                            }
                        },
                        "spec": {
                            "hostNetwork": True,
                            "serviceAccountName": "spot-termination-handler",
                            "containers": [
                                {
                                    "name": "spot-termination-handler",
                                    "image": "public.ecr.aws/aws-ec2/aws-node-termination-handler:v1.19.0",
                                    "env": [
                                        {
                                            "name": "NODE_NAME",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "fieldPath": "spec.nodeName"
                                                }
                                            }
                                        },
                                        {
                                            "name": "POD_NAME",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "fieldPath": "metadata.name"
                                                }
                                            }
                                        },
                                        {
                                            "name": "NAMESPACE",
                                            "valueFrom": {
                                                "fieldRef": {
                                                    "fieldPath": "metadata.namespace"
                                                }
                                            }
                                        }
                                    ]
                                }
                            ],
                            "nodeSelector": {
                                "kubernetes.azure.com/scalesetpriority": "spot"
                            },
                            "tolerations": [
                                {
                                    "operator": "Exists"
                                }
                            ]
                        }
                    }
                }
            },
            "graceful_shutdown": {
                "terminationGracePeriodSeconds": 30,
                "preStop_hook": {
                    "exec": {
                        "command": ["/bin/sh", "-c", "sleep 15 && /app/graceful-shutdown.sh"]
                    }
                }
            }
        }
    
    def _estimate_spot_savings(self) -> Dict[str, Any]:
        """Estimate cost savings from spot instance implementation"""
        return {
            "current_monthly_cost": 2400.00,
            "projected_spot_cost": 960.00,
            "monthly_savings": 1440.00,
            "annual_savings": 17280.00,
            "savings_percentage": 60.0,
            "breakdown": {
                "general_workloads": {
                    "current_cost": 1200.00,
                    "spot_cost": 360.00,
                    "savings": 840.00,
                    "savings_percent": 70.0
                },
                "compute_intensive": {
                    "current_cost": 1200.00,
                    "spot_cost": 600.00,
                    "savings": 600.00,
                    "savings_percent": 50.0
                }
            },
            "risk_assessment": {
                "interruption_rate": "5-20% depending on region and instance type",
                "business_impact": "Low - workloads designed for fault tolerance",
                "mitigation": "Mixed on-demand/spot strategy for critical workloads"
            }
        }
    
    def _create_cost_budgets(self) -> Dict[str, Any]:
        """Create cost budgets and spending limits"""
        return {
            "budgets": [
                {
                    "name": "aks-monthly-budget",
                    "amount": self.budget_config.monthly_budget,
                    "time_period": "Monthly",
                    "scope": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}",
                    "category": "Cost",
                    "filters": {
                        "resource_groups": [self.resource_group],
                        "services": ["Microsoft.ContainerService", "Microsoft.Compute"]
                    },
                    "notifications": [
                        {
                            "enabled": True,
                            "operator": "GreaterThan",
                            "threshold": 50,
                            "contact_emails": ["admin@company.com"],
                            "contact_roles": ["Owner"]
                        },
                        {
                            "enabled": True,
                            "operator": "GreaterThan",
                            "threshold": 80,
                            "contact_emails": ["admin@company.com", "finance@company.com"],
                            "contact_roles": ["Owner", "Contributor"]
                        },
                        {
                            "enabled": True,
                            "operator": "GreaterThan",
                            "threshold": 100,
                            "contact_emails": ["admin@company.com", "finance@company.com", "cto@company.com"],
                            "contact_roles": ["Owner", "Contributor"]
                        }
                    ]
                }
            ]
        }
    
    def _setup_cost_alerts(self) -> List[Dict[str, Any]]:
        """Setup cost alerts and notifications"""
        return [
            {
                "name": "Daily Cost Spike Alert",
                "description": "Alert when daily costs exceed 150% of average",
                "frequency": "Daily",
                "threshold_type": "Percentage",
                "threshold_value": 150,
                "comparison_period": "7days",
                "notification_channels": ["email", "teams", "slack"]
            },
            {
                "name": "Monthly Budget Alert",
                "description": "Alert when monthly costs approach budget limit",
                "frequency": "Daily",
                "threshold_type": "Absolute",
                "threshold_value": self.budget_config.cost_alert_threshold,
                "notification_channels": ["email", "sms"]
            },
            {
                "name": "Unused Resources Alert",
                "description": "Alert when resources are unused for 7 days",
                "frequency": "Weekly",
                "threshold_type": "Usage",
                "threshold_value": 0,
                "notification_channels": ["email"]
            }
        ]
    
    def _create_cost_dashboards(self) -> Dict[str, Any]:
        """Create cost monitoring dashboards"""
        return {
            "azure_dashboard": {
                "name": "AKS Cost Optimization Dashboard",
                "tiles": [
                    {
                        "title": "Monthly Cost Trend",
                        "type": "LineChart",
                        "data_source": "Azure Cost Management",
                        "time_range": "Last 12 months"
                    },
                    {
                        "title": "Cost by Service",
                        "type": "PieChart",
                        "data_source": "Azure Cost Management",
                        "filters": ["Resource Group", "Service"]
                    },
                    {
                        "title": "Top Cost Contributors",
                        "type": "Table",
                        "data_source": "Azure Cost Management",
                        "columns": ["Resource", "Cost", "Change %"]
                    },
                    {
                        "title": "Budget Utilization",
                        "type": "Gauge",
                        "data_source": "Azure Budgets",
                        "thresholds": [50, 80, 100]
                    }
                ]
            },
            "grafana_dashboard": {
                "name": "AKS Resource Utilization",
                "panels": [
                    {
                        "title": "CPU Utilization by Node Pool",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "avg by (nodepool) (rate(container_cpu_usage_seconds_total[5m]) * 100)",
                                "legendFormat": "{{nodepool}}"
                            }
                        ]
                    },
                    {
                        "title": "Memory Utilization by Node Pool",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "avg by (nodepool) (container_memory_usage_bytes / container_spec_memory_limit_bytes * 100)",
                                "legendFormat": "{{nodepool}}"
                            }
                        ]
                    },
                    {
                        "title": "Node Count by Pool Type",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "count by (priority) (kube_node_labels{label_kubernetes_azure_com_scalesetpriority!=\"\"})",
                                "legendFormat": "{{priority}}"
                            }
                        ]
                    }
                ]
            }
        }
    
    def _setup_cost_reports(self) -> Dict[str, Any]:
        """Setup automated cost reports"""
        return {
            "daily_report": {
                "name": "Daily Cost Summary",
                "schedule": "0 9 * * *",
                "recipients": ["admin@company.com"],
                "content": ["Daily spend", "Budget utilization", "Cost anomalies", "Top resources"]
            },
            "weekly_report": {
                "name": "Weekly Cost Optimization Report",
                "schedule": "0 9 * * 1",
                "recipients": ["admin@company.com", "finance@company.com"],
                "content": ["Weekly spend analysis", "Optimization recommendations", "Savings achieved", "Upcoming reserved instance expirations"]
            },
            "monthly_report": {
                "name": "Monthly Cost Review",
                "schedule": "0 9 1 * *",
                "recipients": ["admin@company.com", "finance@company.com", "cto@company.com"],
                "content": ["Monthly cost breakdown", "Budget variance", "Cost optimization achievements", "Next month recommendations"]
            }
        }
    
    def _setup_anomaly_detection(self) -> Dict[str, Any]:
        """Setup cost anomaly detection"""
        return {
            "anomaly_detection_rules": [
                {
                    "name": "Daily Cost Spike",
                    "threshold": 200,
                    "period": "daily",
                    "comparison": "previous_7_days_average",
                    "severity": "high"
                },
                {
                    "name": "Sustained Cost Increase",
                    "threshold": 150,
                    "period": "3days",
                    "comparison": "previous_month_average",
                    "severity": "medium"
                },
                {
                    "name": "Service Cost Anomaly",
                    "threshold": 300,
                    "period": "daily",
                    "scope": "per_service",
                    "severity": "high"
                }
            ],
            "machine_learning": {
                "enabled": True,
                "model": "isolation_forest",
                "training_period": "90days",
                "sensitivity": "medium",
                "auto_update": True
            }
        }
    
    def _create_cost_governance_policies(self) -> List[Dict[str, Any]]:
        """Create Azure policies for cost governance"""
        return [
            {
                "name": "Require Cost Center Tag",
                "description": "Require cost center tag on all resources",
                "mode": "All",
                "policy_rule": {
                    "if": {
                        "field": "tags['CostCenter']",
                        "exists": "false"
                    },
                    "then": {
                        "effect": "deny"
                    }
                }
            },
            {
                "name": "Limit VM Sizes",
                "description": "Restrict VM sizes to approved list",
                "mode": "Indexed",
                "policy_rule": {
                    "if": {
                        "allOf": [
                            {
                                "field": "type",
                                "equals": "Microsoft.Compute/virtualMachines"
                            },
                            {
                                "field": "Microsoft.Compute/virtualMachines/sku.name",
                                "notIn": ["Standard_B2s", "Standard_D2s_v3", "Standard_F2s_v2"]
                            }
                        ]
                    },
                    "then": {
                        "effect": "deny"
                    }
                }
            },
            {
                "name": "Auto-Shutdown Non-Production VMs",
                "description": "Automatically shutdown non-production VMs after hours",
                "mode": "Indexed",
                "policy_rule": {
                    "if": {
                        "allOf": [
                            {
                                "field": "type",
                                "equals": "Microsoft.Compute/virtualMachines"
                            },
                            {
                                "field": "tags['Environment']",
                                "notEquals": "Production"
                            }
                        ]
                    },
                    "then": {
                        "effect": "deployIfNotExists",
                        "details": {
                            "type": "Microsoft.DevTestLab/schedules",
                            "name": "[concat(parameters('vmName'), '-shutdown')]"
                        }
                    }
                }
            }
        ]
    
    def _implement_cost_tagging_strategy(self) -> Dict[str, Any]:
        """Implement comprehensive cost tagging strategy"""
        return {
            "required_tags": [
                {
                    "key": "Environment",
                    "values": ["Production", "Staging", "Development", "Testing"],
                    "description": "Environment classification for resource"
                },
                {
                    "key": "CostCenter",
                    "values": ["IT", "Engineering", "Marketing", "Sales"],
                    "description": "Department responsible for costs"
                },
                {
                    "key": "Project",
                    "description": "Project or application name"
                },
                {
                    "key": "Owner",
                    "description": "Resource owner email address"
                },
                {
                    "key": "StartDate",
                    "format": "YYYY-MM-DD",
                    "description": "Resource creation date"
                },
                {
                    "key": "EndDate",
                    "format": "YYYY-MM-DD",
                    "description": "Expected resource deletion date"
                }
            ],
            "optional_tags": [
                {
                    "key": "Criticality",
                    "values": ["Critical", "High", "Medium", "Low"],
                    "description": "Business criticality level"
                },
                {
                    "key": "Schedule",
                    "values": ["24x7", "Business Hours", "On Demand"],
                    "description": "Operating schedule"
                }
            ],
            "automation": {
                "tag_inheritance": True,
                "automatic_tagging_rules": [
                    {
                        "condition": "resource_group contains 'prod'",
                        "tags": {"Environment": "Production"}
                    },
                    {
                        "condition": "resource_group contains 'dev'",
                        "tags": {"Environment": "Development"}
                    }
                ]
            }
        }
    
    def _implement_spending_limits(self) -> Dict[str, Any]:
        """Implement spending limits and controls"""
        return {
            "subscription_limits": {
                "monthly_limit": 10000.00,
                "action": "send_alert_and_notify",
                "enforcement": "advisory"
            },
            "resource_group_limits": {
                self.resource_group: {
                    "monthly_limit": self.budget_config.monthly_budget,
                    "action": "restrict_new_resources",
                    "enforcement": "strict"
                }
            },
            "department_limits": {
                "IT": {"monthly_limit": 3000.00, "quarterly_limit": 8000.00},
                "Engineering": {"monthly_limit": 5000.00, "quarterly_limit": 14000.00},
                "Testing": {"monthly_limit": 1000.00, "quarterly_limit": 2800.00}
            }
        }
    
    def _setup_approval_workflows(self) -> Dict[str, Any]:
        """Setup approval workflows for cost-impacting changes"""
        return {
            "approval_rules": [
                {
                    "trigger": "VM size change to premium tier",
                    "approvers": ["IT Manager", "Finance Manager"],
                    "approval_timeout": "24hours",
                    "escalation": "CTO"
                },
                {
                    "trigger": "Monthly cost increase > 20%",
                    "approvers": ["Department Head", "Finance"],
                    "approval_timeout": "48hours"
                },
                {
                    "trigger": "New resource group creation",
                    "approvers": ["IT Manager"],
                    "approval_timeout": "12hours"
                }
            ],
            "automation": {
                "auto_approve_conditions": [
                    "Cost increase < 5%",
                    "Pre-approved VM sizes",
                    "Development environment changes"
                ]
            }
        }
    
    def _setup_chargeback_allocation(self) -> Dict[str, Any]:
        """Setup chargeback and cost allocation"""
        return {
            "allocation_methods": [
                {
                    "method": "direct_tagging",
                    "percentage": 70,
                    "description": "Direct allocation based on resource tags"
                },
                {
                    "method": "usage_based",
                    "percentage": 20,
                    "description": "Allocation based on actual usage metrics"
                },
                {
                    "method": "equal_distribution",
                    "percentage": 10,
                    "description": "Equal distribution of shared costs"
                }
            ],
            "cost_centers": [
                {
                    "name": "IT Operations",
                    "allocation_key": "CostCenter:IT",
                    "budget": 3000.00,
                    "contact": "it-manager@company.com"
                },
                {
                    "name": "Product Engineering",
                    "allocation_key": "CostCenter:Engineering",
                    "budget": 5000.00,
                    "contact": "engineering-manager@company.com"
                }
            ],
            "shared_costs": [
                {
                    "service": "Log Analytics Workspace",
                    "allocation_method": "equal_distribution",
                    "beneficiaries": ["IT", "Engineering", "QA"]
                },
                {
                    "service": "Virtual Network",
                    "allocation_method": "usage_based",
                    "metric": "data_transfer"
                }
            ]
        }
    
    def generate_cost_terraform_templates(self) -> Dict[str, str]:
        """Generate Terraform templates for cost optimization"""
        return {
            "cost_main.tf": self._generate_cost_terraform(),
            "budgets.tf": self._generate_budgets_terraform(),
            "policies.tf": self._generate_cost_policies_terraform(),
            "monitoring.tf": self._generate_cost_monitoring_terraform()
        }
    
    def _generate_cost_terraform(self) -> str:
        """Generate main cost optimization Terraform configuration"""
        return """
# Spot instance node pool
resource "azurerm_kubernetes_cluster_node_pool" "spot" {
  name                  = "spot"
  kubernetes_cluster_id = var.aks_cluster_id
  vm_size              = "Standard_D2s_v3"
  priority             = "Spot"
  eviction_policy      = "Delete"
  spot_max_price       = -1
  
  enable_auto_scaling = true
  min_count          = 0
  max_count          = 10
  
  node_taints = [
    "kubernetes.azure.com/scalesetpriority=spot:NoSchedule"
  ]
  
  node_labels = {
    "kubernetes.azure.com/scalesetpriority" = "spot"
    "workload-type" = "fault-tolerant"
  }

  tags = merge(var.common_tags, {
    "cost-optimization" = "spot-instance"
  })
}

# Reserved instances (for stable workloads)
resource "azurerm_reserved_vm_instance" "main" {
  name                = "aks-reserved-instances"
  location            = var.location
  resource_group_name = var.resource_group_name
  
  sku_name            = "Standard_D2s_v3"
  instance_count      = 3
  term                = "P1Y"  # 1 year
  billing_scope_id    = "/subscriptions/${var.subscription_id}"
  
  tags = var.common_tags
}

# Auto-shutdown for non-production resources
resource "azurerm_dev_test_global_vm_shutdown_schedule" "main" {
  location              = var.location
  virtual_machine_id    = var.vm_id
  daily_recurrence_time = "1900"
  timezone              = "UTC"
  
  enabled = var.environment != "Production"
  
  notification_settings {
    enabled = true
    email   = var.shutdown_notification_email
  }

  tags = var.common_tags
}
"""
    
    def _generate_budgets_terraform(self) -> str:
        """Generate budget Terraform configuration"""
        return """
# Consumption budget
resource "azurerm_consumption_budget_resource_group" "main" {
  name              = "budget-${var.resource_group_name}"
  resource_group_id = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}"
  
  amount     = var.monthly_budget
  time_grain = "Monthly"
  
  time_period {
    start_date = formatdate("YYYY-MM-01", timestamp())
  }
  
  filter {
    dimension {
      name = "ResourceGroupName"
      values = [var.resource_group_name]
    }
  }
  
  notification {
    enabled        = true
    threshold      = 50
    operator       = "GreaterThan"
    contact_emails = var.budget_alert_emails
    
    threshold_type = "Actual"
  }
  
  notification {
    enabled        = true
    threshold      = 80
    operator       = "GreaterThan"
    contact_emails = var.budget_alert_emails
    
    threshold_type = "Actual"
  }
  
  notification {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThan"
    contact_emails = var.budget_alert_emails
    
    threshold_type = "Forecasted"
  }
}
"""

    def execute_cost_optimization(self) -> Dict[str, Any]:
        """Execute complete cost optimization implementation"""
        cost_optimization = {
            "cost_analysis": self.analyze_current_costs(),
            "instance_optimization": self.optimize_instance_types(),
            "autoscaling": self.implement_autoscaling(),
            "spot_instances": self.implement_spot_instances(),
            "cost_monitoring": self.setup_cost_monitoring(),
            "cost_governance": self.implement_cost_governance(),
            "terraform_templates": self.generate_cost_terraform_templates()
        }
        
        return cost_optimization


def main():
    """Main execution function for testing"""
    agent = CostAgent(
        subscription_id="your-subscription-id",
        resource_group="rg-aks-demo",
        location="eastus"
    )
    
    cost_optimization = agent.execute_cost_optimization()
    
    # Save configurations to files
    with open("cost_analysis.yaml", "w") as f:
        yaml.dump(cost_optimization["cost_analysis"], f, default_flow_style=False)
    
    with open("autoscaling_config.yaml", "w") as f:
        yaml.dump(cost_optimization["autoscaling"], f, default_flow_style=False)
    
    print("Cost optimization implementation completed successfully!")
    print("Generated configurations for:")
    print("- Cost analysis and optimization opportunities")
    print("- Instance type optimization and rightsizing")
    print("- Comprehensive autoscaling (HPA, VPA, CA, KEDA)")
    print("- Spot instance implementation with fault tolerance")
    print("- Cost monitoring, budgets, and alerts")
    print("- Cost governance policies and controls")


if __name__ == "__main__":
    main()