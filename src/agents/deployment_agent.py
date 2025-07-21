#!/usr/bin/env python3
"""
Deployment Agent - Executes blue-green deployment patterns and advanced deployment strategies
Focuses on zero-downtime deployments, canary releases, and rollback mechanisms for AKS
"""

import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication


@dataclass
class BlueGreenConfig:
    """Blue-Green deployment configuration"""
    enable_blue_green: bool = True
    traffic_split_percentage: int = 10  # Initial traffic to green
    validation_period_minutes: int = 15
    auto_promote: bool = False
    rollback_on_failure: bool = True
    health_check_endpoint: str = "/health"
    success_threshold: int = 95  # Success rate threshold
    max_rollback_time_minutes: int = 5


@dataclass
class CanaryConfig:
    """Canary deployment configuration"""
    enable_canary: bool = True
    initial_canary_percentage: int = 5
    canary_increment: int = 10
    canary_evaluation_interval_minutes: int = 10
    max_canary_percentage: int = 50
    success_criteria: Dict[str, Any] = None
    auto_promote_threshold: float = 99.0
    
    def __post_init__(self):
        if self.success_criteria is None:
            self.success_criteria = {
                "error_rate": {"threshold": 1.0, "comparison": "less_than"},
                "latency_p95": {"threshold": 500, "comparison": "less_than"},
                "success_rate": {"threshold": 99.5, "comparison": "greater_than"}
            }


@dataclass
class RolloutConfig:
    """Rolling deployment configuration"""
    strategy: str = "RollingUpdate"
    max_unavailable: str = "25%"
    max_surge: str = "25%"
    revision_history_limit: int = 10
    progress_deadline_seconds: int = 600
    min_ready_seconds: int = 30


@dataclass
class GitOpsConfig:
    """GitOps deployment configuration"""
    enable_gitops: bool = True
    git_repository: str = ""
    branch: str = "main"
    manifest_path: str = "k8s/manifests"
    sync_policy: str = "automated"
    self_heal: bool = True
    prune: bool = True
    
    def __post_init__(self):
        if not self.git_repository:
            self.git_repository = "https://github.com/company/k8s-manifests.git"


class DeploymentAgent:
    """
    Deployment Agent responsible for:
    - Blue-green deployment implementation
    - Canary deployment strategies
    - Rolling updates with zero-downtime
    - GitOps-based deployments
    - Automated rollback mechanisms
    - Progressive delivery patterns
    """
    
    def __init__(self, subscription_id: str, resource_group: str, cluster_name: str, location: str = "eastus"):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.cluster_name = cluster_name
        self.location = location
        self.credential = DefaultAzureCredential()
        
        # Initialize Azure clients
        self.container_client = ContainerServiceClient(self.credential, subscription_id)
        self.acr_client = ContainerRegistryManagementClient(self.credential, subscription_id)
        
        # Initialize configurations
        self.blue_green_config = BlueGreenConfig()
        self.canary_config = CanaryConfig()
        self.rollout_config = RolloutConfig()
        self.gitops_config = GitOpsConfig()
    
    def implement_blue_green_deployment(self) -> Dict[str, Any]:
        """Implement blue-green deployment pattern"""
        blue_green = {
            "service_configurations": self._generate_blue_green_services(),
            "deployment_manifests": self._generate_blue_green_deployments(),
            "ingress_configurations": self._generate_blue_green_ingress(),
            "traffic_management": self._generate_blue_green_traffic_management(),
            "validation_scripts": self._generate_blue_green_validation(),
            "rollback_procedures": self._generate_blue_green_rollback()
        }
        
        return blue_green
    
    def implement_canary_deployment(self) -> Dict[str, Any]:
        """Implement canary deployment pattern with progressive traffic shifting"""
        canary = {
            "flagger_configuration": self._generate_flagger_config(),
            "canary_manifests": self._generate_canary_manifests(),
            "traffic_splitting": self._generate_canary_traffic_splitting(),
            "metrics_analysis": self._generate_canary_metrics_analysis(),
            "automated_promotion": self._generate_canary_promotion(),
            "rollback_automation": self._generate_canary_rollback()
        }
        
        return canary
    
    def implement_rolling_deployment(self) -> Dict[str, Any]:
        """Implement advanced rolling deployment strategies"""
        rolling = {
            "deployment_strategies": self._generate_rolling_strategies(),
            "pod_disruption_budgets": self._generate_pod_disruption_budgets(),
            "readiness_probes": self._generate_readiness_probes(),
            "health_checks": self._generate_health_checks(),
            "progressive_rollout": self._generate_progressive_rollout()
        }
        
        return rolling
    
    def implement_gitops_deployment(self) -> Dict[str, Any]:
        """Implement GitOps-based deployment with ArgoCD/Flux"""
        gitops = {
            "argocd_configuration": self._generate_argocd_config(),
            "flux_configuration": self._generate_flux_config(),
            "application_manifests": self._generate_gitops_applications(),
            "sync_policies": self._generate_gitops_sync_policies(),
            "webhook_automation": self._generate_gitops_webhooks()
        }
        
        return gitops
    
    def implement_progressive_delivery(self) -> Dict[str, Any]:
        """Implement progressive delivery patterns"""
        progressive = {
            "feature_flags": self._generate_feature_flag_integration(),
            "a_b_testing": self._generate_ab_testing_config(),
            "ring_deployments": self._generate_ring_deployment_config(),
            "dark_launches": self._generate_dark_launch_config(),
            "observability_integration": self._generate_progressive_observability()
        }
        
        return progressive
    
    def implement_deployment_automation(self) -> Dict[str, Any]:
        """Implement deployment automation and CI/CD integration"""
        automation = {
            "azure_devops_pipelines": self._generate_azure_devops_pipelines(),
            "github_actions": self._generate_github_actions(),
            "helm_charts": self._generate_helm_deployment_charts(),
            "kustomize_manifests": self._generate_kustomize_manifests(),
            "deployment_validation": self._generate_deployment_validation()
        }
        
        return automation
    
    def _generate_blue_green_services(self) -> List[Dict[str, Any]]:
        """Generate blue-green service configurations"""
        return [
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "app-service-blue",
                    "namespace": "default",
                    "labels": {
                        "app": "myapp",
                        "version": "blue"
                    }
                },
                "spec": {
                    "selector": {
                        "app": "myapp",
                        "version": "blue"
                    },
                    "ports": [
                        {
                            "port": 80,
                            "targetPort": 8080,
                            "protocol": "TCP"
                        }
                    ],
                    "type": "ClusterIP"
                }
            },
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "app-service-green",
                    "namespace": "default",
                    "labels": {
                        "app": "myapp",
                        "version": "green"
                    }
                },
                "spec": {
                    "selector": {
                        "app": "myapp",
                        "version": "green"
                    },
                    "ports": [
                        {
                            "port": 80,
                            "targetPort": 8080,
                            "protocol": "TCP"
                        }
                    ],
                    "type": "ClusterIP"
                }
            },
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "app-service-active",
                    "namespace": "default",
                    "labels": {
                        "app": "myapp",
                        "role": "active"
                    }
                },
                "spec": {
                    "selector": {
                        "app": "myapp",
                        "version": "blue"  # Initially points to blue
                    },
                    "ports": [
                        {
                            "port": 80,
                            "targetPort": 8080,
                            "protocol": "TCP"
                        }
                    ],
                    "type": "ClusterIP"
                }
            }
        ]
    
    def _generate_blue_green_deployments(self) -> List[Dict[str, Any]]:
        """Generate blue-green deployment manifests"""
        return [
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "myapp-blue",
                    "namespace": "default",
                    "labels": {
                        "app": "myapp",
                        "version": "blue"
                    }
                },
                "spec": {
                    "replicas": 3,
                    "selector": {
                        "matchLabels": {
                            "app": "myapp",
                            "version": "blue"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "myapp",
                                "version": "blue"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "app",
                                    "image": "myregistry.azurecr.io/myapp:v1.0.0",
                                    "ports": [{"containerPort": 8080}],
                                    "resources": {
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        },
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        }
                                    },
                                    "livenessProbe": {
                                        "httpGet": {
                                            "path": self.blue_green_config.health_check_endpoint,
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 10
                                    },
                                    "readinessProbe": {
                                        "httpGet": {
                                            "path": "/ready",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 5,
                                        "periodSeconds": 5
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "myapp-green",
                    "namespace": "default",
                    "labels": {
                        "app": "myapp",
                        "version": "green"
                    }
                },
                "spec": {
                    "replicas": 3,
                    "selector": {
                        "matchLabels": {
                            "app": "myapp",
                            "version": "green"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "myapp",
                                "version": "green"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "app",
                                    "image": "myregistry.azurecr.io/myapp:v2.0.0",
                                    "ports": [{"containerPort": 8080}],
                                    "resources": {
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        },
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        }
                                    },
                                    "livenessProbe": {
                                        "httpGet": {
                                            "path": self.blue_green_config.health_check_endpoint,
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 10
                                    },
                                    "readinessProbe": {
                                        "httpGet": {
                                            "path": "/ready",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 5,
                                        "periodSeconds": 5
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        ]
    
    def _generate_blue_green_ingress(self) -> Dict[str, Any]:
        """Generate ingress configuration for blue-green deployment"""
        return {
            "main_ingress": {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": "myapp-ingress",
                    "namespace": "default",
                    "annotations": {
                        "kubernetes.io/ingress.class": "azure/application-gateway",
                        "appgw.ingress.kubernetes.io/backend-protocol": "http",
                        "appgw.ingress.kubernetes.io/health-probe-path": self.blue_green_config.health_check_endpoint
                    }
                },
                "spec": {
                    "rules": [
                        {
                            "host": "myapp.company.com",
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": "app-service-active",
                                                "port": {"number": 80}
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            "preview_ingress": {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": "myapp-preview-ingress",
                    "namespace": "default",
                    "annotations": {
                        "kubernetes.io/ingress.class": "azure/application-gateway",
                        "appgw.ingress.kubernetes.io/backend-protocol": "http"
                    }
                },
                "spec": {
                    "rules": [
                        {
                            "host": "myapp-preview.company.com",
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": "app-service-green",
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
        }
    
    def _generate_blue_green_traffic_management(self) -> Dict[str, Any]:
        """Generate traffic management for blue-green deployment using Istio"""
        return {
            "virtual_service": {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "VirtualService",
                "metadata": {
                    "name": "myapp-vs",
                    "namespace": "default"
                },
                "spec": {
                    "hosts": ["myapp.company.com"],
                    "gateways": ["myapp-gateway"],
                    "http": [
                        {
                            "match": [
                                {
                                    "headers": {
                                        "canary": {"exact": "true"}
                                    }
                                }
                            ],
                            "route": [
                                {
                                    "destination": {
                                        "host": "app-service-green",
                                        "port": {"number": 80}
                                    }
                                }
                            ]
                        },
                        {
                            "route": [
                                {
                                    "destination": {
                                        "host": "app-service-blue",
                                        "port": {"number": 80}
                                    },
                                    "weight": 90
                                },
                                {
                                    "destination": {
                                        "host": "app-service-green",
                                        "port": {"number": 80}
                                    },
                                    "weight": 10
                                }
                            ]
                        }
                    ]
                }
            },
            "destination_rules": [
                {
                    "apiVersion": "networking.istio.io/v1beta1",
                    "kind": "DestinationRule",
                    "metadata": {
                        "name": "myapp-blue-dr",
                        "namespace": "default"
                    },
                    "spec": {
                        "host": "app-service-blue",
                        "trafficPolicy": {
                            "loadBalancer": {"simple": "LEAST_CONN"},
                            "connectionPool": {
                                "tcp": {"maxConnections": 100},
                                "http": {
                                    "http1MaxPendingRequests": 100,
                                    "maxRequestsPerConnection": 10
                                }
                            },
                            "circuitBreaker": {
                                "consecutiveErrors": 3,
                                "interval": "30s",
                                "baseEjectionTime": "30s"
                            }
                        }
                    }
                },
                {
                    "apiVersion": "networking.istio.io/v1beta1",
                    "kind": "DestinationRule",
                    "metadata": {
                        "name": "myapp-green-dr",
                        "namespace": "default"
                    },
                    "spec": {
                        "host": "app-service-green",
                        "trafficPolicy": {
                            "loadBalancer": {"simple": "LEAST_CONN"},
                            "connectionPool": {
                                "tcp": {"maxConnections": 100},
                                "http": {
                                    "http1MaxPendingRequests": 100,
                                    "maxRequestsPerConnection": 10
                                }
                            },
                            "circuitBreaker": {
                                "consecutiveErrors": 3,
                                "interval": "30s",
                                "baseEjectionTime": "30s"
                            }
                        }
                    }
                }
            ]
        }
    
    def _generate_blue_green_validation(self) -> Dict[str, Any]:
        """Generate validation scripts and health checks for blue-green deployment"""
        return {
            "health_check_script": """#!/bin/bash
# Blue-Green Deployment Validation Script

set -e

BLUE_SERVICE_URL="http://app-service-blue.default.svc.cluster.local"
GREEN_SERVICE_URL="http://app-service-green.default.svc.cluster.local"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/health}"
SUCCESS_THRESHOLD=${SUCCESS_THRESHOLD:-95}
TEST_DURATION=${TEST_DURATION:-300}
CONCURRENT_REQUESTS=${CONCURRENT_REQUESTS:-10}

echo "Starting Blue-Green deployment validation..."

# Function to check service health
check_service_health() {
    local service_url=$1
    local service_name=$2
    
    echo "Checking health for $service_name..."
    
    local success_count=0
    local total_requests=100
    
    for i in $(seq 1 $total_requests); do
        if curl -s -f "$service_url$HEALTH_ENDPOINT" > /dev/null; then
            success_count=$((success_count + 1))
        fi
        sleep 0.1
    done
    
    local success_rate=$((success_count * 100 / total_requests))
    echo "$service_name success rate: $success_rate%"
    
    if [ $success_rate -lt $SUCCESS_THRESHOLD ]; then
        echo "ERROR: $service_name health check failed. Success rate below threshold."
        exit 1
    fi
    
    echo "$service_name health check passed!"
}

# Function to perform load testing
load_test_service() {
    local service_url=$1
    local service_name=$2
    
    echo "Performing load test for $service_name..."
    
    ab -n 1000 -c $CONCURRENT_REQUESTS -t $TEST_DURATION "$service_url/" > /tmp/${service_name}_load_test.log
    
    local avg_response_time=$(grep "Time per request" /tmp/${service_name}_load_test.log | head -1 | awk '{print $4}')
    local requests_per_second=$(grep "Requests per second" /tmp/${service_name}_load_test.log | awk '{print $4}')
    
    echo "$service_name - Average response time: ${avg_response_time}ms"
    echo "$service_name - Requests per second: $requests_per_second"
    
    # Check if average response time is reasonable (< 500ms)
    if (( $(echo "$avg_response_time > 500" | bc -l) )); then
        echo "WARNING: $service_name response time is high"
    fi
}

# Function to compare versions
compare_versions() {
    echo "Comparing Blue and Green versions..."
    
    # Get version info
    BLUE_VERSION=$(curl -s "$BLUE_SERVICE_URL/version" | jq -r '.version')
    GREEN_VERSION=$(curl -s "$GREEN_SERVICE_URL/version" | jq -r '.version')
    
    echo "Blue version: $BLUE_VERSION"
    echo "Green version: $GREEN_VERSION"
    
    # Perform functional tests
    echo "Running functional tests..."
    
    # Test critical endpoints
    for endpoint in "/api/users" "/api/products" "/api/orders"; do
        echo "Testing endpoint: $endpoint"
        
        # Test blue
        blue_response=$(curl -s -w "%{http_code}" "$BLUE_SERVICE_URL$endpoint")
        blue_status=${blue_response: -3}
        
        # Test green
        green_response=$(curl -s -w "%{http_code}" "$GREEN_SERVICE_URL$endpoint")
        green_status=${green_response: -3}
        
        if [ "$blue_status" != "200" ] || [ "$green_status" != "200" ]; then
            echo "ERROR: Endpoint $endpoint failed on one or both versions"
            echo "Blue status: $blue_status, Green status: $green_status"
            exit 1
        fi
        
        echo "Endpoint $endpoint: OK"
    done
}

# Main validation flow
main() {
    echo "=== Blue-Green Deployment Validation ==="
    echo "Validation started at: $(date)"
    
    # Check both services
    check_service_health "$BLUE_SERVICE_URL" "Blue"
    check_service_health "$GREEN_SERVICE_URL" "Green"
    
    # Perform load testing
    load_test_service "$BLUE_SERVICE_URL" "Blue"
    load_test_service "$GREEN_SERVICE_URL" "Green"
    
    # Compare versions and run functional tests
    compare_versions
    
    echo "=== Validation Completed Successfully ==="
    echo "Both Blue and Green services are healthy and ready for traffic switching"
    echo "Validation completed at: $(date)"
}

main "$@"
""",
            "smoke_tests": {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": "smoke-tests",
                    "namespace": "default"
                },
                "data": {
                    "smoke-test.sh": """#!/bin/bash
# Smoke tests for deployment validation

SERVICE_URL=${SERVICE_URL:-"http://app-service-active"}
TIMEOUT=${TIMEOUT:-30}

echo "Running smoke tests against $SERVICE_URL"

# Test 1: Health check
echo "Test 1: Health check"
if ! curl -s -f --max-time $TIMEOUT "$SERVICE_URL/health" > /dev/null; then
    echo "FAIL: Health check failed"
    exit 1
fi
echo "PASS: Health check"

# Test 2: API endpoints
echo "Test 2: API endpoints"
for endpoint in "/api/status" "/api/version"; do
    if ! curl -s -f --max-time $TIMEOUT "$SERVICE_URL$endpoint" > /dev/null; then
        echo "FAIL: $endpoint not responding"
        exit 1
    fi
done
echo "PASS: API endpoints"

# Test 3: Database connectivity
echo "Test 3: Database connectivity"
if ! curl -s -f --max-time $TIMEOUT "$SERVICE_URL/api/health/database" > /dev/null; then
    echo "FAIL: Database connectivity check failed"
    exit 1
fi
echo "PASS: Database connectivity"

echo "All smoke tests passed!"
"""
                }
            }
        }
    
    def _generate_blue_green_rollback(self) -> Dict[str, Any]:
        """Generate automated rollback procedures for blue-green deployment"""
        return {
            "rollback_script": """#!/bin/bash
# Automated Blue-Green Rollback Script

set -e

KUBECTL="kubectl"
NAMESPACE=${NAMESPACE:-"default"}
APP_NAME=${APP_NAME:-"myapp"}
ROLLBACK_TIMEOUT=${ROLLBACK_TIMEOUT:-300}

echo "=== Blue-Green Rollback Initiated ==="
echo "Rollback started at: $(date)"

# Function to get current active version
get_active_version() {
    local selector=$(${KUBECTL} get service app-service-active -n ${NAMESPACE} -o jsonpath='{.spec.selector.version}')
    echo $selector
}

# Function to switch traffic
switch_traffic() {
    local from_version=$1
    local to_version=$2
    
    echo "Switching traffic from $from_version to $to_version..."
    
    # Update active service selector
    ${KUBECTL} patch service app-service-active -n ${NAMESPACE} -p '{"spec":{"selector":{"version":"'$to_version'"}}}'
    
    # Wait for endpoints to be ready
    echo "Waiting for endpoints to be ready..."
    ${KUBECTL} wait --for=condition=ready endpoints/app-service-active -n ${NAMESPACE} --timeout=${ROLLBACK_TIMEOUT}s
    
    echo "Traffic switched successfully!"
}

# Function to verify rollback
verify_rollback() {
    local expected_version=$1
    
    echo "Verifying rollback to $expected_version..."
    
    # Check service selector
    local current_selector=$(get_active_version)
    if [ "$current_selector" != "$expected_version" ]; then
        echo "ERROR: Rollback verification failed. Expected: $expected_version, Got: $current_selector"
        exit 1
    fi
    
    # Run health checks
    echo "Running health checks..."
    local health_check_url="http://app-service-active.${NAMESPACE}.svc.cluster.local/health"
    
    for i in {1..10}; do
        if curl -s -f "$health_check_url" > /dev/null; then
            echo "Health check passed (attempt $i)"
            break
        fi
        
        if [ $i -eq 10 ]; then
            echo "ERROR: Health check failed after 10 attempts"
            exit 1
        fi
        
        echo "Health check failed, retrying in 5 seconds (attempt $i)..."
        sleep 5
    done
    
    echo "Rollback verification successful!"
}

# Main rollback function
main() {
    local current_version=$(get_active_version)
    
    echo "Current active version: $current_version"
    
    if [ "$current_version" == "blue" ]; then
        local rollback_to="green"
    elif [ "$current_version" == "green" ]; then
        local rollback_to="blue"
    else
        echo "ERROR: Unknown current version: $current_version"
        exit 1
    fi
    
    echo "Rolling back from $current_version to $rollback_to"
    
    # Perform rollback
    switch_traffic "$current_version" "$rollback_to"
    
    # Verify rollback
    verify_rollback "$rollback_to"
    
    echo "=== Rollback Completed Successfully ==="
    echo "Rolled back from $current_version to $rollback_to"
    echo "Rollback completed at: $(date)"
}

# Check if this is an emergency rollback
if [ "$1" == "--emergency" ]; then
    echo "EMERGENCY ROLLBACK INITIATED"
    export ROLLBACK_TIMEOUT=60  # Faster timeout for emergency
fi

main "$@"
""",
            "automation": {
                "apiVersion": "batch/v1",
                "kind": "Job",
                "metadata": {
                    "name": "bg-rollback-job",
                    "namespace": "default"
                },
                "spec": {
                    "template": {
                        "spec": {
                            "restartPolicy": "Never",
                            "containers": [
                                {
                                    "name": "rollback",
                                    "image": "bitnami/kubectl:latest",
                                    "command": ["/bin/bash"],
                                    "args": ["/scripts/rollback.sh"],
                                    "volumeMounts": [
                                        {
                                            "name": "rollback-scripts",
                                            "mountPath": "/scripts"
                                        }
                                    ]
                                }
                            ],
                            "volumes": [
                                {
                                    "name": "rollback-scripts",
                                    "configMap": {
                                        "name": "rollback-scripts",
                                        "defaultMode": 0o755
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    
    def _generate_flagger_config(self) -> Dict[str, Any]:
        """Generate Flagger configuration for automated canary deployments"""
        return {
            "flagger_canary": {
                "apiVersion": "flagger.app/v1beta1",
                "kind": "Canary",
                "metadata": {
                    "name": "myapp-canary",
                    "namespace": "default"
                },
                "spec": {
                    "targetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": "myapp"
                    },
                    "progressDeadlineSeconds": 60,
                    "service": {
                        "port": 80,
                        "targetPort": 8080,
                        "gateways": ["myapp-gateway"],
                        "hosts": ["myapp.company.com"]
                    },
                    "analysis": {
                        "interval": f"{self.canary_config.canary_evaluation_interval_minutes}m",
                        "threshold": 5,
                        "maxWeight": self.canary_config.max_canary_percentage,
                        "stepWeight": self.canary_config.canary_increment,
                        "metrics": [
                            {
                                "name": "request-success-rate",
                                "thresholdRange": {
                                    "min": self.canary_config.success_criteria["success_rate"]["threshold"]
                                },
                                "interval": "1m"
                            },
                            {
                                "name": "request-duration",
                                "thresholdRange": {
                                    "max": self.canary_config.success_criteria["latency_p95"]["threshold"]
                                },
                                "interval": "1m"
                            }
                        ],
                        "webhooks": [
                            {
                                "name": "acceptance-test",
                                "type": "pre-rollout",
                                "url": "http://flagger-loadtester.test/",
                                "timeout": "30s",
                                "metadata": {
                                    "type": "bash",
                                    "cmd": "curl -sd 'test' http://myapp-canary.default/token | grep token"
                                }
                            },
                            {
                                "name": "load-test",
                                "url": "http://flagger-loadtester.test/",
                                "timeout": "5s",
                                "metadata": {
                                    "cmd": "hey -z 1m -q 10 -c 2 http://myapp-canary.default/"
                                }
                            }
                        ]
                    }
                }
            },
            "metric_templates": [
                {
                    "apiVersion": "flagger.app/v1beta1",
                    "kind": "MetricTemplate",
                    "metadata": {
                        "name": "request-success-rate",
                        "namespace": "default"
                    },
                    "spec": {
                        "provider": {
                            "type": "prometheus",
                            "address": "http://prometheus:9090"
                        },
                        "query": 'sum(rate(istio_requests_total{reporter="destination",destination_service_name="{{args.service}}", destination_service_namespace="{{args.namespace}}",response_code!~"5.*"}[{{args.interval}}])) / sum(rate(istio_requests_total{reporter="destination",destination_service_name="{{args.service}}",destination_service_namespace="{{args.namespace}}"}[{{args.interval}}]))'
                    }
                },
                {
                    "apiVersion": "flagger.app/v1beta1",
                    "kind": "MetricTemplate",
                    "metadata": {
                        "name": "request-duration",
                        "namespace": "default"
                    },
                    "spec": {
                        "provider": {
                            "type": "prometheus",
                            "address": "http://prometheus:9090"
                        },
                        "query": 'histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket{reporter="destination",destination_service_name="{{args.service}}",destination_service_namespace="{{args.namespace}}"}[{{args.interval}}])) by (le))'
                    }
                }
            ]
        }
    
    def _generate_canary_manifests(self) -> List[Dict[str, Any]]:
        """Generate canary deployment manifests"""
        return [
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "myapp",
                    "namespace": "default",
                    "labels": {
                        "app": "myapp"
                    }
                },
                "spec": {
                    "replicas": 3,
                    "selector": {
                        "matchLabels": {
                            "app": "myapp"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "myapp"
                            },
                            "annotations": {
                                "prometheus.io/scrape": "true",
                                "prometheus.io/port": "8080",
                                "prometheus.io/path": "/metrics"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "myapp",
                                    "image": "myregistry.azurecr.io/myapp:1.0.0",
                                    "ports": [
                                        {
                                            "containerPort": 8080,
                                            "name": "http",
                                            "protocol": "TCP"
                                        }
                                    ],
                                    "resources": {
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        },
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        }
                                    },
                                    "livenessProbe": {
                                        "httpGet": {
                                            "path": "/healthz",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 10,
                                        "timeoutSeconds": 5,
                                        "failureThreshold": 3
                                    },
                                    "readinessProbe": {
                                        "httpGet": {
                                            "path": "/readyz",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 5,
                                        "periodSeconds": 5,
                                        "timeoutSeconds": 3,
                                        "failureThreshold": 3
                                    },
                                    "env": [
                                        {
                                            "name": "VERSION",
                                            "value": "1.0.0"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        ]
    
    def _generate_canary_traffic_splitting(self) -> Dict[str, Any]:
        """Generate traffic splitting configuration for canary deployment"""
        return {
            "istio_virtual_service": {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "VirtualService",
                "metadata": {
                    "name": "myapp-vs",
                    "namespace": "default"
                },
                "spec": {
                    "hosts": ["myapp.company.com"],
                    "gateways": ["myapp-gateway"],
                    "http": [
                        {
                            "match": [
                                {
                                    "headers": {
                                        "x-canary-user": {"exact": "true"}
                                    }
                                }
                            ],
                            "route": [
                                {
                                    "destination": {
                                        "host": "myapp-canary",
                                        "port": {"number": 80}
                                    }
                                }
                            ]
                        },
                        {
                            "route": [
                                {
                                    "destination": {
                                        "host": "myapp-primary",
                                        "port": {"number": 80}
                                    },
                                    "weight": 95
                                },
                                {
                                    "destination": {
                                        "host": "myapp-canary",
                                        "port": {"number": 80}
                                    },
                                    "weight": 5
                                }
                            ]
                        }
                    ]
                }
            },
            "nginx_ingress_canary": {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": "myapp-canary-ingress",
                    "namespace": "default",
                    "annotations": {
                        "kubernetes.io/ingress.class": "nginx",
                        "nginx.ingress.kubernetes.io/canary": "true",
                        "nginx.ingress.kubernetes.io/canary-weight": str(self.canary_config.initial_canary_percentage),
                        "nginx.ingress.kubernetes.io/canary-by-header": "x-canary",
                        "nginx.ingress.kubernetes.io/canary-by-header-value": "always"
                    }
                },
                "spec": {
                    "rules": [
                        {
                            "host": "myapp.company.com",
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": "myapp-canary",
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
        }
    
    def _generate_canary_metrics_analysis(self) -> Dict[str, Any]:
        """Generate metrics analysis configuration for canary deployment"""
        return {
            "prometheus_rules": {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "PrometheusRule",
                "metadata": {
                    "name": "canary-analysis-rules",
                    "namespace": "default"
                },
                "spec": {
                    "groups": [
                        {
                            "name": "canary.rules",
                            "interval": "30s",
                            "rules": [
                                {
                                    "alert": "CanaryHighErrorRate",
                                    "expr": 'sum(rate(http_requests_total{job="myapp-canary",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="myapp-canary"}[5m])) > 0.01',
                                    "for": "2m",
                                    "labels": {
                                        "severity": "critical",
                                        "deployment": "canary"
                                    },
                                    "annotations": {
                                        "summary": "Canary deployment has high error rate",
                                        "description": "Canary deployment error rate is above 1% for more than 2 minutes"
                                    }
                                },
                                {
                                    "alert": "CanaryHighLatency",
                                    "expr": 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="myapp-canary"}[5m])) by (le)) > 0.5',
                                    "for": "2m",
                                    "labels": {
                                        "severity": "warning",
                                        "deployment": "canary"
                                    },
                                    "annotations": {
                                        "summary": "Canary deployment has high latency",
                                        "description": "Canary deployment 95th percentile latency is above 500ms for more than 2 minutes"
                                    }
                                }
                            ]
                        }
                    ]
                }
            },
            "grafana_dashboard": {
                "dashboard": {
                    "title": "Canary Deployment Analysis",
                    "panels": [
                        {
                            "title": "Request Rate",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": 'sum(rate(http_requests_total{job="myapp-primary"}[5m]))',
                                    "legendFormat": "Primary"
                                },
                                {
                                    "expr": 'sum(rate(http_requests_total{job="myapp-canary"}[5m]))',
                                    "legendFormat": "Canary"
                                }
                            ]
                        },
                        {
                            "title": "Error Rate",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": 'sum(rate(http_requests_total{job="myapp-primary",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="myapp-primary"}[5m]))',
                                    "legendFormat": "Primary Error Rate"
                                },
                                {
                                    "expr": 'sum(rate(http_requests_total{job="myapp-canary",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="myapp-canary"}[5m]))',
                                    "legendFormat": "Canary Error Rate"
                                }
                            ]
                        },
                        {
                            "title": "Response Time",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="myapp-primary"}[5m])) by (le))',
                                    "legendFormat": "Primary P95"
                                },
                                {
                                    "expr": 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="myapp-canary"}[5m])) by (le))',
                                    "legendFormat": "Canary P95"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    
    def _generate_canary_promotion(self) -> Dict[str, Any]:
        """Generate automated canary promotion configuration"""
        return {
            "promotion_webhook": """#!/bin/bash
# Automated Canary Promotion Script

set -e

NAMESPACE=${NAMESPACE:-"default"}
CANARY_NAME=${CANARY_NAME:-"myapp-canary"}
PROMOTION_THRESHOLD=${PROMOTION_THRESHOLD:-99.0}
MONITORING_DURATION=${MONITORING_DURATION:-300}

echo "=== Canary Promotion Analysis ==="
echo "Analysis started at: $(date)"

# Function to get canary metrics
get_canary_metrics() {
    local query_url="http://prometheus:9090/api/v1/query"
    
    # Get success rate
    local success_rate_query='sum(rate(http_requests_total{job="myapp-canary",status!~"5.."}[5m])) / sum(rate(http_requests_total{job="myapp-canary"}[5m])) * 100'
    local success_rate=$(curl -s "$query_url?query=$success_rate_query" | jq -r '.data.result[0].value[1]')
    
    # Get error rate
    local error_rate_query='sum(rate(http_requests_total{job="myapp-canary",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="myapp-canary"}[5m])) * 100'
    local error_rate=$(curl -s "$query_url?query=$error_rate_query" | jq -r '.data.result[0].value[1]')
    
    # Get latency
    local latency_query='histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="myapp-canary"}[5m])) by (le))'
    local latency=$(curl -s "$query_url?query=$latency_query" | jq -r '.data.result[0].value[1]')
    
    echo "Current metrics:"
    echo "  Success rate: ${success_rate}%"
    echo "  Error rate: ${error_rate}%"
    echo "  95th percentile latency: ${latency}s"
    
    # Check if metrics meet promotion criteria
    if (( $(echo "$success_rate >= $PROMOTION_THRESHOLD" | bc -l) )); then
        echo "SUCCESS: Canary metrics meet promotion criteria"
        return 0
    else
        echo "FAIL: Canary metrics do not meet promotion criteria"
        return 1
    fi
}

# Function to promote canary
promote_canary() {
    echo "Promoting canary to production..."
    
    # Update Flagger canary to promote
    kubectl patch canary $CANARY_NAME -n $NAMESPACE --type='json' -p='[{"op": "replace", "path": "/spec/analysis/maxWeight", "value": 100}]'
    
    # Wait for promotion to complete
    echo "Waiting for canary promotion to complete..."
    kubectl wait --for=condition=Promoted canary/$CANARY_NAME -n $NAMESPACE --timeout=600s
    
    echo "Canary promoted successfully!"
}

# Function to monitor canary performance
monitor_canary() {
    echo "Monitoring canary performance for $MONITORING_DURATION seconds..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + MONITORING_DURATION))
    local check_interval=30
    
    while [ $(date +%s) -lt $end_time ]; do
        if get_canary_metrics; then
            echo "Metrics check passed at $(date)"
        else
            echo "ERROR: Metrics check failed at $(date)"
            echo "Aborting promotion due to failed metrics"
            return 1
        fi
        
        sleep $check_interval
    done
    
    echo "Monitoring completed successfully"
    return 0
}

# Main promotion logic
main() {
    echo "Starting canary promotion analysis..."
    
    # Monitor canary performance
    if monitor_canary; then
        echo "Canary performance is stable, proceeding with promotion"
        promote_canary
        echo "=== Canary Promotion Completed ==="
    else
        echo "=== Canary Promotion Aborted ==="
        echo "Canary will be rolled back automatically"
        exit 1
    fi
}

main "$@"
""",
            "promotion_job": {
                "apiVersion": "batch/v1",
                "kind": "Job",
                "metadata": {
                    "name": "canary-promotion-job",
                    "namespace": "default"
                },
                "spec": {
                    "template": {
                        "spec": {
                            "restartPolicy": "Never",
                            "containers": [
                                {
                                    "name": "promote-canary",
                                    "image": "bitnami/kubectl:latest",
                                    "command": ["/bin/bash"],
                                    "args": ["/scripts/promote-canary.sh"],
                                    "env": [
                                        {
                                            "name": "PROMOTION_THRESHOLD",
                                            "value": str(self.canary_config.auto_promote_threshold)
                                        }
                                    ],
                                    "volumeMounts": [
                                        {
                                            "name": "promotion-scripts",
                                            "mountPath": "/scripts"
                                        }
                                    ]
                                }
                            ],
                            "volumes": [
                                {
                                    "name": "promotion-scripts",
                                    "configMap": {
                                        "name": "promotion-scripts",
                                        "defaultMode": 0o755
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    
    def _generate_canary_rollback(self) -> Dict[str, Any]:
        """Generate automated canary rollback configuration"""
        return {
            "rollback_webhook": """#!/bin/bash
# Automated Canary Rollback Script

set -e

NAMESPACE=${NAMESPACE:-"default"}
CANARY_NAME=${CANARY_NAME:-"myapp-canary"}
ERROR_THRESHOLD=${ERROR_THRESHOLD:-5.0}
LATENCY_THRESHOLD=${LATENCY_THRESHOLD:-1.0}

echo "=== Canary Rollback Initiated ==="
echo "Rollback analysis started at: $(date)"

# Function to check if rollback is needed
needs_rollback() {
    local query_url="http://prometheus:9090/api/v1/query"
    
    # Check error rate
    local error_rate_query='sum(rate(http_requests_total{job="myapp-canary",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="myapp-canary"}[5m])) * 100'
    local error_rate=$(curl -s "$query_url?query=$error_rate_query" | jq -r '.data.result[0].value[1]' | head -1)
    
    # Check latency
    local latency_query='histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="myapp-canary"}[5m])) by (le))'
    local latency=$(curl -s "$query_url?query=$latency_query" | jq -r '.data.result[0].value[1]' | head -1)
    
    echo "Current canary metrics:"
    echo "  Error rate: ${error_rate}%"
    echo "  95th percentile latency: ${latency}s"
    
    # Check if rollback is needed
    if (( $(echo "$error_rate > $ERROR_THRESHOLD" | bc -l) )) || (( $(echo "$latency > $LATENCY_THRESHOLD" | bc -l) )); then
        echo "ALERT: Canary metrics exceed thresholds - rollback needed"
        return 0
    else
        echo "INFO: Canary metrics are within acceptable limits"
        return 1
    fi
}

# Function to perform rollback
perform_rollback() {
    echo "Performing canary rollback..."
    
    # Stop the canary analysis
    kubectl patch canary $CANARY_NAME -n $NAMESPACE --type='json' -p='[{"op": "replace", "path": "/spec/analysis/threshold", "value": 0}]'
    
    # Set traffic weight to 0 for canary
    kubectl patch canary $CANARY_NAME -n $NAMESPACE --type='json' -p='[{"op": "replace", "path": "/spec/analysis/maxWeight", "value": 0}]'
    
    # Wait for rollback to complete
    echo "Waiting for canary rollback to complete..."
    kubectl wait --for=condition=Failed canary/$CANARY_NAME -n $NAMESPACE --timeout=300s || true
    
    echo "Canary rollback completed successfully!"
}

# Function to send alerts
send_rollback_alert() {
    local reason=$1
    
    echo "Sending rollback alert..."
    
    # Send to webhook (Slack, Teams, etc.)
    local webhook_url="${ALERT_WEBHOOK_URL}"
    if [ ! -z "$webhook_url" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 Canary Rollback Alert 🚨\\nApplication: $CANARY_NAME\\nNamespace: $NAMESPACE\\nReason: $reason\\nTime: $(date)\"}" \
            "$webhook_url"
    fi
    
    # Log to stdout
    echo "ALERT: Canary rollback performed - $reason"
}

# Main rollback logic
main() {
    if needs_rollback; then
        local rollback_reason="Canary metrics exceeded thresholds"
        
        perform_rollback
        send_rollback_alert "$rollback_reason"
        
        echo "=== Canary Rollback Completed ==="
        echo "Rollback reason: $rollback_reason"
        echo "Rollback completed at: $(date)"
        
        exit 1  # Exit with error to indicate rollback occurred
    else
        echo "=== No Rollback Needed ==="
        echo "Canary metrics are healthy"
        exit 0
    fi
}

main "$@"
""",
            "alert_rules": {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "PrometheusRule",
                "metadata": {
                    "name": "canary-rollback-rules",
                    "namespace": "default"
                },
                "spec": {
                    "groups": [
                        {
                            "name": "canary.rollback",
                            "interval": "15s",
                            "rules": [
                                {
                                    "alert": "CanaryRollbackRequired",
                                    "expr": 'sum(rate(http_requests_total{job="myapp-canary",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="myapp-canary"}[5m])) > 0.05',
                                    "for": "1m",
                                    "labels": {
                                        "severity": "critical",
                                        "action": "rollback"
                                    },
                                    "annotations": {
                                        "summary": "Canary rollback required due to high error rate",
                                        "description": "Canary deployment has error rate > 5% for 1 minute",
                                        "runbook_url": "https://runbooks.company.com/canary-rollback"
                                    }
                                },
                                {
                                    "alert": "CanaryHighLatencyRollback",
                                    "expr": 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="myapp-canary"}[5m])) by (le)) > 1.0',
                                    "for": "2m",
                                    "labels": {
                                        "severity": "warning",
                                        "action": "rollback"
                                    },
                                    "annotations": {
                                        "summary": "Canary rollback recommended due to high latency",
                                        "description": "Canary deployment 95th percentile latency > 1s for 2 minutes"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        }
    
    def _generate_rolling_strategies(self) -> List[Dict[str, Any]]:
        """Generate advanced rolling deployment strategies"""
        return [
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "myapp-rolling",
                    "namespace": "default"
                },
                "spec": {
                    "replicas": 6,
                    "strategy": {
                        "type": self.rollout_config.strategy,
                        "rollingUpdate": {
                            "maxUnavailable": self.rollout_config.max_unavailable,
                            "maxSurge": self.rollout_config.max_surge
                        }
                    },
                    "minReadySeconds": self.rollout_config.min_ready_seconds,
                    "progressDeadlineSeconds": self.rollout_config.progress_deadline_seconds,
                    "revisionHistoryLimit": self.rollout_config.revision_history_limit,
                    "selector": {
                        "matchLabels": {
                            "app": "myapp"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "myapp"
                            }
                        },
                        "spec": {
                            "terminationGracePeriodSeconds": 30,
                            "containers": [
                                {
                                    "name": "myapp",
                                    "image": "myregistry.azurecr.io/myapp:latest",
                                    "ports": [{"containerPort": 8080}],
                                    "resources": {
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        },
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        }
                                    },
                                    "livenessProbe": {
                                        "httpGet": {
                                            "path": "/healthz",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 10,
                                        "timeoutSeconds": 5,
                                        "failureThreshold": 3
                                    },
                                    "readinessProbe": {
                                        "httpGet": {
                                            "path": "/readyz",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 5,
                                        "periodSeconds": 5,
                                        "timeoutSeconds": 3,
                                        "failureThreshold": 3
                                    },
                                    "lifecycle": {
                                        "preStop": {
                                            "exec": {
                                                "command": ["/bin/sh", "-c", "sleep 15"]
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        ]
    
    def _generate_pod_disruption_budgets(self) -> List[Dict[str, Any]]:
        """Generate Pod Disruption Budgets for zero-downtime deployments"""
        return [
            {
                "apiVersion": "policy/v1",
                "kind": "PodDisruptionBudget",
                "metadata": {
                    "name": "myapp-pdb",
                    "namespace": "default"
                },
                "spec": {
                    "minAvailable": "50%",
                    "selector": {
                        "matchLabels": {
                            "app": "myapp"
                        }
                    }
                }
            },
            {
                "apiVersion": "policy/v1",
                "kind": "PodDisruptionBudget",
                "metadata": {
                    "name": "critical-app-pdb",
                    "namespace": "default"
                },
                "spec": {
                    "minAvailable": 2,
                    "selector": {
                        "matchLabels": {
                            "app": "critical-app",
                            "tier": "frontend"
                        }
                    }
                }
            }
        ]
    
    def _generate_readiness_probes(self) -> List[Dict[str, Any]]:
        """Generate advanced readiness probe configurations"""
        return [
            {
                "name": "http_readiness_probe",
                "httpGet": {
                    "path": "/health/ready",
                    "port": 8080,
                    "httpHeaders": [
                        {
                            "name": "Custom-Health-Check",
                            "value": "readiness"
                        }
                    ]
                },
                "initialDelaySeconds": 10,
                "periodSeconds": 5,
                "timeoutSeconds": 3,
                "successThreshold": 1,
                "failureThreshold": 3
            },
            {
                "name": "exec_readiness_probe",
                "exec": {
                    "command": [
                        "/bin/sh",
                        "-c",
                        "curl -f http://localhost:8080/health && nc -z database 5432"
                    ]
                },
                "initialDelaySeconds": 15,
                "periodSeconds": 10,
                "timeoutSeconds": 5,
                "failureThreshold": 2
            },
            {
                "name": "tcp_readiness_probe",
                "tcpSocket": {
                    "port": 8080
                },
                "initialDelaySeconds": 5,
                "periodSeconds": 10,
                "timeoutSeconds": 1,
                "failureThreshold": 3
            }
        ]
    
    def _generate_health_checks(self) -> Dict[str, Any]:
        """Generate comprehensive health check configurations"""
        return {
            "startup_probe": {
                "httpGet": {
                    "path": "/health/startup",
                    "port": 8080
                },
                "initialDelaySeconds": 10,
                "periodSeconds": 10,
                "timeoutSeconds": 5,
                "failureThreshold": 30,  # Allow up to 5 minutes for startup
                "successThreshold": 1
            },
            "liveness_probe": {
                "httpGet": {
                    "path": "/health/live",
                    "port": 8080
                },
                "initialDelaySeconds": 30,
                "periodSeconds": 10,
                "timeoutSeconds": 5,
                "failureThreshold": 3,
                "successThreshold": 1
            },
            "readiness_probe": {
                "httpGet": {
                    "path": "/health/ready",
                    "port": 8080
                },
                "initialDelaySeconds": 5,
                "periodSeconds": 5,
                "timeoutSeconds": 3,
                "failureThreshold": 3,
                "successThreshold": 1
            },
            "health_endpoints": {
                "startup": {
                    "description": "Checks if application has started successfully",
                    "checks": ["database_migration", "config_loading", "dependency_initialization"]
                },
                "liveness": {
                    "description": "Checks if application is alive and responsive",
                    "checks": ["basic_functionality", "memory_usage", "thread_deadlock"]
                },
                "readiness": {
                    "description": "Checks if application is ready to serve traffic",
                    "checks": ["database_connectivity", "external_service_availability", "cache_warmup"]
                }
            }
        }
    
    def _generate_progressive_rollout(self) -> Dict[str, Any]:
        """Generate progressive rollout configuration"""
        return {
            "argo_rollout": {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "Rollout",
                "metadata": {
                    "name": "myapp-rollout",
                    "namespace": "default"
                },
                "spec": {
                    "replicas": 6,
                    "strategy": {
                        "canary": {
                            "steps": [
                                {"setWeight": 10},
                                {"pause": {"duration": "2m"}},
                                {"setWeight": 20},
                                {"pause": {"duration": "2m"}},
                                {"setWeight": 40},
                                {"pause": {"duration": "2m"}},
                                {"setWeight": 60},
                                {"pause": {"duration": "2m"}},
                                {"setWeight": 80},
                                {"pause": {"duration": "2m"}}
                            ],
                            "trafficRouting": {
                                "istio": {
                                    "virtualService": {
                                        "name": "myapp-vs",
                                        "routes": ["primary"]
                                    }
                                }
                            },
                            "analysis": {
                                "templates": [
                                    {
                                        "templateName": "success-rate",
                                        "args": [
                                            {
                                                "name": "service-name",
                                                "value": "myapp-canary"
                                            }
                                        ]
                                    }
                                ],
                                "startingStep": 2,
                                "args": [
                                    {
                                        "name": "success-rate-threshold",
                                        "value": "95"
                                    }
                                ]
                            }
                        }
                    },
                    "selector": {
                        "matchLabels": {
                            "app": "myapp"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "myapp"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "myapp",
                                    "image": "myregistry.azurecr.io/myapp:latest",
                                    "ports": [{"containerPort": 8080}],
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
            },
            "analysis_template": {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "AnalysisTemplate",
                "metadata": {
                    "name": "success-rate",
                    "namespace": "default"
                },
                "spec": {
                    "args": [
                        {
                            "name": "service-name",
                            "value": "myapp-canary"
                        },
                        {
                            "name": "success-rate-threshold",
                            "value": "95"
                        }
                    ],
                    "metrics": [
                        {
                            "name": "success-rate",
                            "interval": "1m",
                            "count": 5,
                            "successCondition": "result[0] >= {{args.success-rate-threshold}}",
                            "provider": {
                                "prometheus": {
                                    "address": "http://prometheus:9090",
                                    "query": 'sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[5m])) / sum(rate(http_requests_total{service="{{args.service-name}}"}[5m])) * 100'
                                }
                            }
                        }
                    ]
                }
            }
        }
    
    def _generate_argocd_config(self) -> Dict[str, Any]:
        """Generate ArgoCD GitOps configuration"""
        return {
            "application": {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "Application",
                "metadata": {
                    "name": "myapp",
                    "namespace": "argocd"
                },
                "spec": {
                    "project": "default",
                    "source": {
                        "repoURL": self.gitops_config.git_repository,
                        "targetRevision": self.gitops_config.branch,
                        "path": self.gitops_config.manifest_path
                    },
                    "destination": {
                        "server": "https://kubernetes.default.svc",
                        "namespace": "default"
                    },
                    "syncPolicy": {
                        "automated": {
                            "prune": self.gitops_config.prune,
                            "selfHeal": self.gitops_config.self_heal
                        } if self.gitops_config.sync_policy == "automated" else None,
                        "syncOptions": ["CreateNamespace=true"]
                    }
                }
            },
            "app_project": {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "AppProject",
                "metadata": {
                    "name": "production",
                    "namespace": "argocd"
                },
                "spec": {
                    "description": "Production applications",
                    "sourceRepos": [
                        self.gitops_config.git_repository,
                        "https://github.com/company/helm-charts"
                    ],
                    "destinations": [
                        {
                            "namespace": "default",
                            "server": "https://kubernetes.default.svc"
                        },
                        {
                            "namespace": "production",
                            "server": "https://kubernetes.default.svc"
                        }
                    ],
                    "clusterResourceWhitelist": [
                        {
                            "group": "",
                            "kind": "Namespace"
                        }
                    ],
                    "roles": [
                        {
                            "name": "admin",
                            "description": "Admin access to production applications",
                            "policies": [
                                "p, proj:production:admin, applications, *, production/*, allow",
                                "p, proj:production:admin, repositories, *, *, allow"
                            ],
                            "groups": ["argocd-admins"]
                        },
                        {
                            "name": "developer",
                            "description": "Developer access to production applications",
                            "policies": [
                                "p, proj:production:developer, applications, get, production/*, allow",
                                "p, proj:production:developer, applications, sync, production/*, allow"
                            ],
                            "groups": ["argocd-developers"]
                        }
                    ]
                }
            }
        }
    
    def _generate_flux_config(self) -> Dict[str, Any]:
        """Generate Flux GitOps configuration"""
        return {
            "git_repository": {
                "apiVersion": "source.toolkit.fluxcd.io/v1beta1",
                "kind": "GitRepository",
                "metadata": {
                    "name": "myapp-repo",
                    "namespace": "flux-system"
                },
                "spec": {
                    "interval": "1m",
                    "ref": {
                        "branch": self.gitops_config.branch
                    },
                    "url": self.gitops_config.git_repository
                }
            },
            "kustomization": {
                "apiVersion": "kustomize.toolkit.fluxcd.io/v1beta1",
                "kind": "Kustomization",
                "metadata": {
                    "name": "myapp",
                    "namespace": "flux-system"
                },
                "spec": {
                    "interval": "5m",
                    "path": f"./{self.gitops_config.manifest_path}",
                    "prune": self.gitops_config.prune,
                    "sourceRef": {
                        "kind": "GitRepository",
                        "name": "myapp-repo"
                    },
                    "validation": "client",
                    "healthChecks": [
                        {
                            "apiVersion": "apps/v1",
                            "kind": "Deployment",
                            "name": "myapp",
                            "namespace": "default"
                        }
                    ]
                }
            },
            "helm_repository": {
                "apiVersion": "source.toolkit.fluxcd.io/v1beta1",
                "kind": "HelmRepository",
                "metadata": {
                    "name": "bitnami",
                    "namespace": "flux-system"
                },
                "spec": {
                    "interval": "10m",
                    "url": "https://charts.bitnami.com/bitnami"
                }
            },
            "helm_release": {
                "apiVersion": "helm.toolkit.fluxcd.io/v2beta1",
                "kind": "HelmRelease",
                "metadata": {
                    "name": "myapp-helm",
                    "namespace": "default"
                },
                "spec": {
                    "interval": "5m",
                    "chart": {
                        "spec": {
                            "chart": "myapp",
                            "version": "1.0.0",
                            "sourceRef": {
                                "kind": "HelmRepository",
                                "name": "company-charts",
                                "namespace": "flux-system"
                            }
                        }
                    },
                    "values": {
                        "image": {
                            "repository": "myregistry.azurecr.io/myapp",
                            "tag": "latest"
                        },
                        "replicas": 3,
                        "resources": {
                            "requests": {
                                "cpu": "100m",
                                "memory": "128Mi"
                            }
                        }
                    }
                }
            }
        }
    
    def generate_deployment_terraform_templates(self) -> Dict[str, str]:
        """Generate Terraform templates for deployment infrastructure"""
        return {
            "deployment_main.tf": self._generate_deployment_terraform(),
            "container_registry.tf": self._generate_acr_terraform(),
            "gitops.tf": self._generate_gitops_terraform()
        }
    
    def _generate_deployment_terraform(self) -> str:
        """Generate main deployment Terraform configuration"""
        return """
# Azure Container Registry for storing container images
resource "azurerm_container_registry" "main" {
  name                = "acr${replace(var.resource_group_name, "-", "")}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Premium"
  admin_enabled       = false

  identity {
    type = "SystemAssigned"
  }

  network_rule_set {
    default_action = "Deny"
    
    virtual_network {
      action    = "Allow"
      subnet_id = var.aks_subnet_id
    }
  }

  public_network_access_enabled = false

  tags = var.common_tags
}

# Private endpoint for ACR
resource "azurerm_private_endpoint" "acr" {
  name                = "pe-acr-${var.resource_group_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoints_subnet_id

  private_service_connection {
    name                           = "psc-acr"
    private_connection_resource_id = azurerm_container_registry.main.id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "pdzg-acr"
    private_dns_zone_ids = [azurerm_private_dns_zone.acr.id]
  }

  tags = var.common_tags
}

# Private DNS zone for ACR
resource "azurerm_private_dns_zone" "acr" {
  name                = "privatelink.azurecr.io"
  resource_group_name = var.resource_group_name

  tags = var.common_tags
}

# Link private DNS zone to VNet
resource "azurerm_private_dns_zone_virtual_network_link" "acr" {
  name                  = "acr-dns-link"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.acr.name
  virtual_network_id    = var.virtual_network_id

  tags = var.common_tags
}

# Role assignment for AKS to pull from ACR
resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = var.aks_kubelet_identity_object_id
}

# Azure DevOps Service Connection for ACR
resource "azuredevops_serviceendpoint_azurecr" "main" {
  project_id            = var.azdo_project_id
  service_endpoint_name = "ACR-${azurerm_container_registry.main.name}"
  
  resource_group        = var.resource_group_name
  azurecr_spn_tenantid  = data.azurerm_client_config.current.tenant_id
  azurecr_name         = azurerm_container_registry.main.name
  azurecr_subscription_id = data.azurerm_client_config.current.subscription_id
  azurecr_subscription_name = "Production"
}

data "azurerm_client_config" "current" {}
"""
    
    def _generate_acr_terraform(self) -> str:
        """Generate Azure Container Registry Terraform configuration"""
        return """
# ACR tasks for automated builds
resource "azurerm_container_registry_task" "main" {
  name                  = "build-task"
  container_registry_id = azurerm_container_registry.main.id
  
  platform {
    os = "Linux"
  }

  docker_step {
    dockerfile_path      = "Dockerfile"
    context_path         = "https://github.com/company/myapp.git"
    context_access_token = var.github_token
    image_names          = ["myapp:{{.Run.ID}}"]
  }

  source_trigger {
    name           = "defaultSourceTriggerName"
    events         = ["commit"]
    repository_url = "https://github.com/company/myapp.git"
    source_type    = "Github"
    
    authentication {
      token      = var.github_token
      token_type = "PAT"
    }
  }

  tags = var.common_tags
}

# ACR webhook for deployment triggers
resource "azurerm_container_registry_webhook" "main" {
  name                = "deploymentWebhook"
  resource_group_name = var.resource_group_name
  registry_name       = azurerm_container_registry.main.name
  location            = var.location

  service_uri    = var.webhook_service_uri
  status         = "enabled"
  scope          = "myapp:*"
  actions        = ["push"]
  custom_headers = {
    "Content-Type" = "application/json"
  }

  tags = var.common_tags
}

# ACR scope map for limited access
resource "azurerm_container_registry_scope_map" "ci_cd" {
  name                    = "ci-cd-scope-map"
  container_registry_name = azurerm_container_registry.main.name
  resource_group_name     = var.resource_group_name
  
  actions = [
    "repositories/myapp/content/read",
    "repositories/myapp/content/write",
    "repositories/myapp/metadata/read",
    "repositories/myapp/metadata/write"
  ]
}

# ACR token for CI/CD pipelines
resource "azurerm_container_registry_token" "ci_cd" {
  name                    = "ci-cd-token"
  container_registry_name = azurerm_container_registry.main.name
  resource_group_name     = var.resource_group_name
  scope_map_id           = azurerm_container_registry_scope_map.ci_cd.id
  enabled                = true
}
"""
    
    def _generate_gitops_terraform(self) -> str:
        """Generate GitOps Terraform configuration"""
        return """
# Namespace for ArgoCD
resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }
}

# ArgoCD installation using Helm
resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = "5.46.7"
  namespace  = kubernetes_namespace.argocd.metadata[0].name

  values = [
    yamlencode({
      global = {
        image = {
          tag = "v2.8.4"
        }
      }
      
      configs = {
        params = {
          "server.insecure" = true
        }
      }
      
      server = {
        service = {
          type = "LoadBalancer"
          annotations = {
            "service.beta.kubernetes.io/azure-load-balancer-internal" = "true"
          }
        }
        
        ingress = {
          enabled = true
          ingressClassName = "azure/application-gateway"
          hosts = ["argocd.company.com"]
          tls = [{
            secretName = "argocd-server-tls"
            hosts = ["argocd.company.com"]
          }]
        }
      }
      
      repoServer = {
        resources = {
          limits = {
            cpu = "1000m"
            memory = "1024Mi"
          }
          requests = {
            cpu = "500m"
            memory = "512Mi"
          }
        }
      }
      
      applicationSet = {
        enabled = true
      }
    })
  ]

  depends_on = [kubernetes_namespace.argocd]
}

# Flux installation
resource "kubernetes_namespace" "flux_system" {
  metadata {
    name = "flux-system"
  }
}

resource "helm_release" "flux" {
  name       = "flux2"
  repository = "https://fluxcd-community.github.io/helm-charts"
  chart      = "flux2"
  version    = "2.10.6"
  namespace  = kubernetes_namespace.flux_system.metadata[0].name

  values = [
    yamlencode({
      cli = {
        image = "fluxcd/flux-cli:v2.1.2"
      }
      
      controllers = {
        source = {
          create = true
        }
        kustomize = {
          create = true
        }
        helm = {
          create = true
        }
        notification = {
          create = true
        }
      }
    })
  ]

  depends_on = [kubernetes_namespace.flux_system]
}

# Git repository secret for private repos
resource "kubernetes_secret" "git_repo" {
  metadata {
    name      = "git-repo-secret"
    namespace = kubernetes_namespace.flux_system.metadata[0].name
  }

  type = "Opaque"

  data = {
    username = base64encode(var.git_username)
    password = base64encode(var.git_token)
  }
}
"""

    def execute_deployment_implementation(self) -> Dict[str, Any]:
        """Execute complete deployment implementation"""
        deployment_config = {
            "blue_green": self.implement_blue_green_deployment(),
            "canary": self.implement_canary_deployment(),
            "rolling": self.implement_rolling_deployment(),
            "gitops": self.implement_gitops_deployment(),
            "progressive_delivery": self.implement_progressive_delivery(),
            "automation": self.implement_deployment_automation(),
            "terraform_templates": self.generate_deployment_terraform_templates()
        }
        
        return deployment_config


def main():
    """Main execution function for testing"""
    agent = DeploymentAgent(
        subscription_id="your-subscription-id",
        resource_group="rg-aks-demo",
        cluster_name="aks-demo",
        location="eastus"
    )
    
    deployment_config = agent.execute_deployment_implementation()
    
    # Save configurations to files
    with open("blue_green_config.yaml", "w") as f:
        yaml.dump(deployment_config["blue_green"], f, default_flow_style=False)
    
    with open("canary_config.yaml", "w") as f:
        yaml.dump(deployment_config["canary"], f, default_flow_style=False)
    
    print("Deployment implementation completed successfully!")
    print("Generated configurations for:")
    print("- Blue-green deployment with automated validation")
    print("- Canary deployment with progressive traffic shifting")
    print("- Rolling deployment with zero-downtime strategies")
    print("- GitOps deployment with ArgoCD and Flux")
    print("- Progressive delivery patterns")
    print("- CI/CD automation and validation")


if __name__ == "__main__":
    main()