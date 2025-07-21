#!/usr/bin/env python3
"""
Monitoring Agent - Sets up distributed tracing, metrics, and alerting
Focuses on comprehensive observability for AKS clusters using Azure Monitor and open-source tools
"""

import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient


@dataclass
class MonitoringConfig:
    """Core monitoring configuration"""
    enable_azure_monitor: bool = True
    enable_prometheus: bool = True
    enable_grafana: bool = True
    enable_jaeger: bool = True
    enable_application_insights: bool = True
    log_retention_days: int = 30
    metrics_retention_days: int = 90
    enable_container_insights: bool = True


@dataclass
class AlertingConfig:
    """Alerting configuration"""
    enable_smart_alerts: bool = True
    alert_notification_channels: List[str] = None
    critical_alert_threshold: int = 2
    warning_alert_threshold: int = 5
    enable_auto_resolution: bool = True
    
    def __post_init__(self):
        if self.alert_notification_channels is None:
            self.alert_notification_channels = ["email", "teams", "pagerduty"]


@dataclass
class TracingConfig:
    """Distributed tracing configuration"""
    enable_distributed_tracing: bool = True
    tracing_backend: str = "jaeger"  # jaeger, zipkin, or azure
    sample_rate: float = 0.1
    enable_service_map: bool = True
    trace_retention_days: int = 7


@dataclass
class MetricsConfig:
    """Metrics collection configuration"""
    enable_custom_metrics: bool = True
    metrics_scrape_interval: str = "30s"
    enable_business_metrics: bool = True
    enable_sli_slo_monitoring: bool = True
    prometheus_storage_retention: str = "15d"


class MonitoringAgent:
    """
    Monitoring Agent responsible for:
    - Azure Monitor and Log Analytics setup
    - Prometheus and Grafana deployment
    - Distributed tracing with Jaeger
    - Application Insights integration
    - Alert rules and notification setup
    - SLI/SLO monitoring and dashboards
    """
    
    def __init__(self, subscription_id: str, resource_group: str, cluster_name: str, location: str = "eastus"):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.cluster_name = cluster_name
        self.location = location
        self.credential = DefaultAzureCredential()
        
        # Initialize Azure clients
        self.monitor_client = MonitorManagementClient(self.credential, subscription_id)
        self.log_analytics_client = LogAnalyticsManagementClient(self.credential, subscription_id)
        self.app_insights_client = ApplicationInsightsManagementClient(self.credential, subscription_id)
        
        # Initialize configurations
        self.monitoring_config = MonitoringConfig()
        self.alerting_config = AlertingConfig()
        self.tracing_config = TracingConfig()
        self.metrics_config = MetricsConfig()
    
    def setup_azure_monitoring(self) -> Dict[str, Any]:
        """Setup Azure Monitor, Log Analytics, and Application Insights"""
        azure_monitoring = {
            "log_analytics_workspace": self._create_log_analytics_workspace(),
            "application_insights": self._create_application_insights(),
            "container_insights": self._configure_container_insights(),
            "azure_monitor_integration": self._configure_azure_monitor_integration(),
            "diagnostic_settings": self._configure_diagnostic_settings()
        }
        
        return azure_monitoring
    
    def setup_prometheus_stack(self) -> Dict[str, Any]:
        """Setup Prometheus monitoring stack"""
        prometheus_stack = {
            "prometheus_operator": self._deploy_prometheus_operator(),
            "prometheus_config": self._configure_prometheus(),
            "service_monitors": self._create_service_monitors(),
            "alert_manager": self._configure_alert_manager(),
            "recording_rules": self._create_prometheus_recording_rules()
        }
        
        return prometheus_stack
    
    def setup_grafana_dashboards(self) -> Dict[str, Any]:
        """Setup Grafana with comprehensive dashboards"""
        grafana_setup = {
            "grafana_deployment": self._deploy_grafana(),
            "data_sources": self._configure_grafana_datasources(),
            "dashboards": self._create_grafana_dashboards(),
            "dashboard_provisioning": self._configure_dashboard_provisioning(),
            "user_management": self._configure_grafana_users()
        }
        
        return grafana_setup
    
    def setup_distributed_tracing(self) -> Dict[str, Any]:
        """Setup distributed tracing with Jaeger"""
        tracing_setup = {
            "jaeger_deployment": self._deploy_jaeger(),
            "tracing_configuration": self._configure_distributed_tracing(),
            "service_mesh_tracing": self._configure_istio_tracing(),
            "application_tracing": self._configure_application_tracing(),
            "trace_analysis": self._setup_trace_analysis()
        }
        
        return tracing_setup
    
    def setup_alerting_rules(self) -> Dict[str, Any]:
        """Setup comprehensive alerting rules"""
        alerting = {
            "prometheus_alerts": self._create_prometheus_alert_rules(),
            "azure_monitor_alerts": self._create_azure_monitor_alerts(),
            "notification_channels": self._configure_notification_channels(),
            "escalation_policies": self._create_escalation_policies(),
            "alert_correlation": self._configure_alert_correlation()
        }
        
        return alerting
    
    def setup_sli_slo_monitoring(self) -> Dict[str, Any]:
        """Setup SLI/SLO monitoring and error budgets"""
        sli_slo = {
            "sli_definitions": self._define_service_level_indicators(),
            "slo_configurations": self._configure_service_level_objectives(),
            "error_budget_monitoring": self._setup_error_budget_monitoring(),
            "slo_dashboards": self._create_slo_dashboards(),
            "burn_rate_alerts": self._create_burn_rate_alerts()
        }
        
        return sli_slo
    
    def _create_log_analytics_workspace(self) -> Dict[str, Any]:
        """Create Log Analytics workspace"""
        return {
            "name": f"log-{self.cluster_name}",
            "location": self.location,
            "sku": "PerGB2018",
            "retention_in_days": self.monitoring_config.log_retention_days,
            "daily_quota_gb": 10,
            "features": {
                "legacy_free_tier": False,
                "search_version": 1,
                "enable_log_access_using_only_resource_permissions": True
            },
            "saved_searches": [
                {
                    "name": "Kubernetes Errors",
                    "category": "Kubernetes",
                    "query": 'ContainerLog | where LogEntry contains "error" or LogEntry contains "ERROR" | summarize count() by Computer, ContainerName'
                },
                {
                    "name": "High CPU Usage",
                    "category": "Performance",
                    "query": 'Perf | where CounterName == "% Processor Time" | where CounterValue > 80 | summarize avg(CounterValue) by Computer'
                }
            ]
        }
    
    def _create_application_insights(self) -> Dict[str, Any]:
        """Create Application Insights instance"""
        return {
            "name": f"ai-{self.cluster_name}",
            "location": self.location,
            "application_type": "web",
            "retention_in_days": 90,
            "sampling_percentage": 100,
            "features": {
                "enable_live_metrics": True,
                "enable_snapshot_debugger": False,
                "enable_profiler": True
            },
            "continuous_export": {
                "enabled": True,
                "destination_type": "Blob",
                "export_configuration": [
                    {
                        "record_types": ["Requests", "Event", "Exception", "Metric", "PageView"],
                        "destination_account": f"aiexport{self.resource_group.replace('-', '')}"
                    }
                ]
            }
        }
    
    def _configure_container_insights(self) -> Dict[str, Any]:
        """Configure Container Insights for AKS monitoring"""
        return {
            "enabled": True,
            "workspace_resource_id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/log-{self.cluster_name}",
            "data_collection": {
                "enable_container_log_v2": True,
                "streams": [
                    "Microsoft-ContainerLog",
                    "Microsoft-ContainerLogV2",
                    "Microsoft-KubeEvents",
                    "Microsoft-KubePodInventory",
                    "Microsoft-KubeNodeInventory",
                    "Microsoft-KubeServices",
                    "Microsoft-InsightsMetrics"
                ]
            },
            "cost_preset": "Standard",
            "log_collection_settings": {
                "stdout_enabled": True,
                "stderr_enabled": True,
                "env_var_collection_enabled": True
            }
        }
    
    def _configure_azure_monitor_integration(self) -> Dict[str, Any]:
        """Configure Azure Monitor integration"""
        return {
            "managed_prometheus": {
                "enabled": True,
                "workspace_id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Monitor/accounts/ama-{self.cluster_name}"
            },
            "managed_grafana": {
                "enabled": True,
                "workspace_name": f"amg-{self.cluster_name}",
                "location": self.location,
                "sku": "Standard"
            },
            "data_collection_rules": [
                {
                    "name": f"dcr-{self.cluster_name}",
                    "data_flows": [
                        {
                            "streams": ["Microsoft-PrometheusMetrics"],
                            "destinations": ["MonitoringAccount1"]
                        }
                    ],
                    "destinations": {
                        "monitor_account": [
                            {
                                "account_resource_id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Monitor/accounts/ama-{self.cluster_name}",
                                "name": "MonitoringAccount1"
                            }
                        ]
                    }
                }
            ]
        }
    
    def _configure_diagnostic_settings(self) -> List[Dict[str, Any]]:
        """Configure diagnostic settings for various Azure resources"""
        return [
            {
                "name": f"diag-{self.cluster_name}-aks",
                "target_resource_id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.ContainerService/managedClusters/{self.cluster_name}",
                "workspace_id": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/log-{self.cluster_name}",
                "logs": [
                    {"category": "kube-apiserver", "enabled": True},
                    {"category": "kube-audit", "enabled": True},
                    {"category": "kube-audit-admin", "enabled": True},
                    {"category": "kube-controller-manager", "enabled": True},
                    {"category": "kube-scheduler", "enabled": True},
                    {"category": "cluster-autoscaler", "enabled": True},
                    {"category": "guard", "enabled": True}
                ],
                "metrics": [
                    {"category": "AllMetrics", "enabled": True}
                ]
            }
        ]
    
    def _deploy_prometheus_operator(self) -> Dict[str, Any]:
        """Deploy Prometheus Operator"""
        return {
            "helm_release": {
                "name": "prometheus-operator",
                "repository": "https://prometheus-community.github.io/helm-charts",
                "chart": "kube-prometheus-stack",
                "version": "54.0.1",
                "namespace": "monitoring",
                "values": {
                    "prometheus": {
                        "prometheusSpec": {
                            "retention": self.metrics_config.prometheus_storage_retention,
                            "scrapeInterval": self.metrics_config.metrics_scrape_interval,
                            "evaluationInterval": "30s",
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "2Gi"},
                                "limits": {"cpu": "2", "memory": "8Gi"}
                            },
                            "storageSpec": {
                                "volumeClaimTemplate": {
                                    "spec": {
                                        "storageClassName": "managed-csi-premium",
                                        "accessModes": ["ReadWriteOnce"],
                                        "resources": {"requests": {"storage": "100Gi"}}
                                    }
                                }
                            },
                            "additionalScrapeConfigs": self._get_additional_scrape_configs()
                        }
                    },
                    "grafana": {
                        "enabled": True,
                        "persistence": {
                            "enabled": True,
                            "storageClassName": "managed-csi",
                            "size": "10Gi"
                        },
                        "adminPassword": "admin123!",  # Should be from secret in production
                        "resources": {
                            "requests": {"cpu": "100m", "memory": "128Mi"},
                            "limits": {"cpu": "500m", "memory": "512Mi"}
                        }
                    },
                    "alertmanager": {
                        "alertmanagerSpec": {
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "500m", "memory": "512Mi"}
                            }
                        }
                    }
                }
            }
        }
    
    def _configure_prometheus(self) -> Dict[str, Any]:
        """Configure Prometheus settings"""
        return {
            "global_config": {
                "scrape_interval": self.metrics_config.metrics_scrape_interval,
                "evaluation_interval": "30s",
                "external_labels": {
                    "cluster": self.cluster_name,
                    "region": self.location
                }
            },
            "rule_files": [
                "/etc/prometheus/rules/*.yml"
            ],
            "scrape_configs": [
                {
                    "job_name": "kubernetes-apiservers",
                    "kubernetes_sd_configs": [{"role": "endpoints"}],
                    "scheme": "https",
                    "tls_config": {"ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"},
                    "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_namespace", "__meta_kubernetes_service_name", "__meta_kubernetes_endpoint_port_name"],
                            "action": "keep",
                            "regex": "default;kubernetes;https"
                        }
                    ]
                },
                {
                    "job_name": "kubernetes-nodes",
                    "kubernetes_sd_configs": [{"role": "node"}],
                    "scheme": "https",
                    "tls_config": {"ca_file": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"},
                    "bearer_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
                    "relabel_configs": [
                        {
                            "action": "labelmap",
                            "regex": "__meta_kubernetes_node_label_(.+)"
                        }
                    ]
                }
            ]
        }
    
    def _get_additional_scrape_configs(self) -> List[Dict[str, Any]]:
        """Get additional Prometheus scrape configurations"""
        return [
            {
                "job_name": "istio-mesh",
                "kubernetes_sd_configs": [{"role": "endpoints", "namespaces": {"names": ["istio-system"]}}],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_service_name", "__meta_kubernetes_endpoint_port_name"],
                        "action": "keep",
                        "regex": "istio-proxy;http-monitoring"
                    }
                ]
            },
            {
                "job_name": "application-metrics",
                "kubernetes_sd_configs": [{"role": "pod"}],
                "relabel_configs": [
                    {
                        "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"],
                        "action": "keep",
                        "regex": "true"
                    },
                    {
                        "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_path"],
                        "action": "replace",
                        "target_label": "__metrics_path__",
                        "regex": "(.+)"
                    }
                ]
            }
        ]
    
    def _create_service_monitors(self) -> List[Dict[str, Any]]:
        """Create ServiceMonitor resources for automatic discovery"""
        return [
            {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": "istio-service-monitor",
                    "namespace": "monitoring"
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": "istiod"
                        }
                    },
                    "endpoints": [
                        {
                            "port": "http-monitoring",
                            "interval": "30s",
                            "path": "/stats/prometheus"
                        }
                    ]
                }
            },
            {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": "application-service-monitor",
                    "namespace": "monitoring"
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "monitoring": "enabled"
                        }
                    },
                    "endpoints": [
                        {
                            "port": "metrics",
                            "interval": "30s",
                            "path": "/metrics"
                        }
                    ]
                }
            }
        ]
    
    def _configure_alert_manager(self) -> Dict[str, Any]:
        """Configure AlertManager"""
        return {
            "global": {
                "smtp_smarthost": "smtp.company.com:587",
                "smtp_from": "alerts@company.com"
            },
            "route": {
                "group_by": ["alertname"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "default-receiver",
                "routes": [
                    {
                        "match": {"severity": "critical"},
                        "receiver": "critical-alerts",
                        "group_wait": "0s",
                        "repeat_interval": "5m"
                    },
                    {
                        "match": {"alertname": "Watchdog"},
                        "receiver": "null"
                    }
                ]
            },
            "receivers": [
                {
                    "name": "default-receiver",
                    "email_configs": [
                        {
                            "to": "devops@company.com",
                            "subject": "Alert: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}"
                        }
                    ]
                },
                {
                    "name": "critical-alerts",
                    "email_configs": [
                        {
                            "to": "oncall@company.com",
                            "subject": "🚨 CRITICAL: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}"
                        }
                    ],
                    "webhook_configs": [
                        {
                            "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                            "send_resolved": True
                        }
                    ]
                },
                {
                    "name": "null"
                }
            ]
        }
    
    def _create_prometheus_recording_rules(self) -> List[Dict[str, Any]]:
        """Create Prometheus recording rules for performance"""
        return [
            {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "PrometheusRule",
                "metadata": {
                    "name": "recording-rules",
                    "namespace": "monitoring"
                },
                "spec": {
                    "groups": [
                        {
                            "name": "k8s.rules",
                            "interval": "30s",
                            "rules": [
                                {
                                    "record": "cluster:namespace:pod_memory:active:kube_pod_container_resource_requests",
                                    "expr": "kube_pod_container_resource_requests{resource=\"memory\"} * on (namespace, pod) group_left() max by (namespace, pod) ((kube_pod_status_phase{phase=~\"Pending|Running\"} == 1))"
                                },
                                {
                                    "record": "cluster:namespace:pod_cpu:active:kube_pod_container_resource_requests",
                                    "expr": "kube_pod_container_resource_requests{resource=\"cpu\"} * on (namespace, pod) group_left() max by (namespace, pod) ((kube_pod_status_phase{phase=~\"Pending|Running\"} == 1))"
                                }
                            ]
                        },
                        {
                            "name": "application.rules",
                            "interval": "30s",
                            "rules": [
                                {
                                    "record": "http_request_rate_5m",
                                    "expr": "sum(rate(http_requests_total[5m])) by (job, instance, method, code)"
                                },
                                {
                                    "record": "http_request_duration_p95",
                                    "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (job, instance, le))"
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    
    def _deploy_jaeger(self) -> Dict[str, Any]:
        """Deploy Jaeger for distributed tracing"""
        return {
            "helm_release": {
                "name": "jaeger",
                "repository": "https://jaegertracing.github.io/helm-charts",
                "chart": "jaeger",
                "version": "0.71.11",
                "namespace": "tracing",
                "values": {
                    "provisionDataStore": {
                        "cassandra": False,
                        "elasticsearch": True
                    },
                    "elasticsearch": {
                        "replicas": 3,
                        "minimumMasterNodes": 2,
                        "resources": {
                            "requests": {"cpu": "1", "memory": "2Gi"},
                            "limits": {"cpu": "2", "memory": "4Gi"}
                        }
                    },
                    "collector": {
                        "resources": {
                            "requests": {"cpu": "100m", "memory": "128Mi"},
                            "limits": {"cpu": "1", "memory": "1Gi"}
                        },
                        "service": {
                            "type": "ClusterIP",
                            "grpc": {"port": 14250},
                            "http": {"port": 14268}
                        }
                    },
                    "query": {
                        "resources": {
                            "requests": {"cpu": "100m", "memory": "128Mi"},
                            "limits": {"cpu": "500m", "memory": "512Mi"}
                        },
                        "service": {
                            "type": "ClusterIP",
                            "port": 16686
                        },
                        "ingress": {
                            "enabled": True,
                            "ingressClassName": "azure/application-gateway",
                            "hosts": [f"jaeger.{self.cluster_name}.company.com"]
                        }
                    },
                    "agent": {
                        "daemonset": {
                            "useHostPort": True
                        },
                        "resources": {
                            "requests": {"cpu": "50m", "memory": "64Mi"},
                            "limits": {"cpu": "200m", "memory": "256Mi"}
                        }
                    }
                }
            }
        }
    
    def _configure_distributed_tracing(self) -> Dict[str, Any]:
        """Configure distributed tracing settings"""
        return {
            "sampling_strategies": {
                "default_strategy": {
                    "type": "probabilistic",
                    "param": self.tracing_config.sample_rate
                },
                "per_service_strategies": [
                    {
                        "service": "critical-service",
                        "type": "probabilistic",
                        "param": 1.0
                    },
                    {
                        "service": "batch-service",
                        "type": "probabilistic", 
                        "param": 0.01
                    }
                ]
            },
            "jaeger_config": {
                "reporter": {
                    "logSpans": False,
                    "localAgentHostPort": "jaeger-agent:6831"
                },
                "sampler": {
                    "type": "probabilistic",
                    "param": self.tracing_config.sample_rate
                }
            }
        }

    def generate_monitoring_terraform_templates(self) -> Dict[str, str]:
        """Generate Terraform templates for monitoring infrastructure"""
        return {
            "monitoring_main.tf": self._generate_monitoring_terraform(),
            "log_analytics.tf": self._generate_log_analytics_terraform(),
            "application_insights.tf": self._generate_app_insights_terraform(),
            "alerts.tf": self._generate_alerts_terraform()
        }
    
    def _generate_monitoring_terraform(self) -> str:
        """Generate main monitoring Terraform configuration"""
        return f"""
# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {{
  name                = "log-{self.cluster_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = {self.monitoring_config.log_retention_days}
  daily_quota_gb      = 10

  tags = var.common_tags
}}

# Application Insights
resource "azurerm_application_insights" "main" {{
  name                = "ai-{self.cluster_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id
  retention_in_days   = 90

  tags = var.common_tags
}}

# Azure Monitor Workspace (for Managed Prometheus)
resource "azurerm_monitor_workspace" "main" {{
  name                = "ama-{self.cluster_name}"
  resource_group_name = var.resource_group_name
  location            = var.location

  tags = var.common_tags
}}

# Data Collection Endpoint
resource "azurerm_monitor_data_collection_endpoint" "main" {{
  name                = "dce-{self.cluster_name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  kind                = "Linux"

  tags = var.common_tags
}}

# Data Collection Rule
resource "azurerm_monitor_data_collection_rule" "main" {{
  name                = "dcr-{self.cluster_name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  
  data_collection_endpoint_id = azurerm_monitor_data_collection_endpoint.main.id

  destinations {{
    monitor_account {{
      monitor_account_id = azurerm_monitor_workspace.main.id
      name              = "MonitoringAccount1"
    }}
  }}

  data_flow {{
    streams      = ["Microsoft-PrometheusMetrics"]
    destinations = ["MonitoringAccount1"]
  }}

  data_sources {{
    prometheus_forwarder {{
      streams = ["Microsoft-PrometheusMetrics"]
      name    = "PrometheusDataSource"
    }}
  }}

  tags = var.common_tags
}}

# Grafana Workspace
resource "azurerm_dashboard_grafana" "main" {{
  name                              = "amg-{self.cluster_name}"
  resource_group_name               = var.resource_group_name
  location                          = var.location
  api_key_enabled                   = true
  deterministic_outbound_ip_enabled = true
  public_network_access_enabled     = true

  identity {{
    type = "SystemAssigned"
  }}

  azure_monitor_workspace_integrations {{
    resource_id = azurerm_monitor_workspace.main.id
  }}

  tags = var.common_tags
}}
"""

    def execute_monitoring_implementation(self) -> Dict[str, Any]:
        """Execute complete monitoring implementation"""
        monitoring_config = {
            "azure_monitoring": self.setup_azure_monitoring(),
            "prometheus_stack": self.setup_prometheus_stack(),
            "grafana_dashboards": self.setup_grafana_dashboards(),
            "distributed_tracing": self.setup_distributed_tracing(),
            "alerting_rules": self.setup_alerting_rules(),
            "sli_slo_monitoring": self.setup_sli_slo_monitoring(),
            "terraform_templates": self.generate_monitoring_terraform_templates()
        }
        
        return monitoring_config


def main():
    """Main execution function for testing"""
    agent = MonitoringAgent(
        subscription_id="your-subscription-id",
        resource_group="rg-aks-demo",
        cluster_name="aks-demo",
        location="eastus"
    )
    
    monitoring_config = agent.execute_monitoring_implementation()
    
    # Save configurations to files
    with open("monitoring_config.yaml", "w") as f:
        yaml.dump(monitoring_config, f, default_flow_style=False)
    
    print("Monitoring implementation completed successfully!")
    print("Generated configurations for:")
    print("- Azure Monitor, Log Analytics, and Application Insights")
    print("- Prometheus and Grafana stack with dashboards")
    print("- Distributed tracing with Jaeger")
    print("- Comprehensive alerting rules and notifications")
    print("- SLI/SLO monitoring and error budget tracking")


if __name__ == "__main__":
    main()