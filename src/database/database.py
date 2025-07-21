#!/usr/bin/env python3
"""
Database Layer - Vector embeddings, cost optimization data, and persistent storage
Uses SQLite for local storage and ChromaDB for vector embeddings
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import numpy as np
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ResourceTemplate:
    """Resource template with cost optimization data"""
    id: str
    name: str
    resource_type: str
    description: str
    cost_tier: str  # "ultra-low", "low", "medium", "high"
    monthly_cost_estimate: float
    configuration: Dict[str, Any]
    deployment_time_minutes: int
    use_cases: List[str]
    prerequisites: List[str]
    post_deployment_guide: str
    tags: List[str]

@dataclass
class DeploymentHistory:
    """Deployment history record"""
    id: str
    user_request: str
    resources_created: List[Dict[str, Any]]
    total_cost: float
    deployment_time: datetime
    status: str  # "success", "failed", "in_progress"
    user_feedback: Optional[str] = None

class IntelligentDatabase:
    """
    Intelligent database for the AI DevOps Agent
    - Vector embeddings for semantic search
    - Cost optimization data
    - Deployment history and learning
    - Resource templates and best practices
    """
    
    def __init__(self, db_path: str = "ai_devops_agent.db"):
        self.db_path = db_path
        self.db_dir = Path(db_path).parent
        self.db_dir.mkdir(exist_ok=True)
        
        # Initialize SQLite
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Initialize ChromaDB for vector embeddings
        self.chroma_client = chromadb.PersistentClient(path=str(self.db_dir / "chroma_db"))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create collections
        self.resource_collection = self.chroma_client.get_or_create_collection(
            name="resource_templates",
            embedding_function=self.embedding_function
        )
        
        self.deployment_collection = self.chroma_client.get_or_create_collection(
            name="deployment_history", 
            embedding_function=self.embedding_function
        )
        
        self._initialize_tables()
        self._populate_initial_data()
    
    def _initialize_tables(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Resource templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                description TEXT,
                cost_tier TEXT,
                monthly_cost_estimate REAL,
                configuration TEXT,
                deployment_time_minutes INTEGER,
                use_cases TEXT,
                prerequisites TEXT,
                post_deployment_guide TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Deployment history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployment_history (
                id TEXT PRIMARY KEY,
                user_request TEXT NOT NULL,
                resources_created TEXT,
                total_cost REAL,
                deployment_time TIMESTAMP,
                status TEXT,
                user_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cost optimization data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_optimization (
                resource_type TEXT,
                region TEXT,
                instance_type TEXT,
                spot_savings_percent REAL,
                reserved_savings_percent REAL,
                current_price_per_hour REAL,
                spot_price_per_hour REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (resource_type, region, instance_type)
            )
        """)
        
        # User preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT,
                preference_key TEXT,
                preference_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, preference_key)
            )
        """)
        
        self.conn.commit()
    
    def _populate_initial_data(self):
        """Populate database with initial resource templates and cost data"""
        
        # Check if data already exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM resource_templates")
        if cursor.fetchone()[0] > 0:
            return  # Data already exists
        
        # Ultra-low cost templates
        ultra_low_templates = [
            ResourceTemplate(
                id="aks-ultra-low",
                name="Ultra-Low Cost AKS Cluster",
                resource_type="aks",
                description="Minimal AKS cluster with spot instances for development/testing",
                cost_tier="ultra-low",
                monthly_cost_estimate=45.0,
                configuration={
                    "node_count": 1,
                    "vm_size": "Standard_B2s",
                    "enable_spot_instances": True,
                    "spot_percentage": 100,
                    "enable_autoscaling": True,
                    "min_nodes": 0,
                    "max_nodes": 3,
                    "network_policy": "calico",
                    "enable_private_cluster": False  # Public for cost savings
                },
                deployment_time_minutes=12,
                use_cases=["Development", "Testing", "Learning", "Proof of Concepts"],
                prerequisites=["Resource Group"],
                post_deployment_guide="""
# 🚀 Getting Started with Your Ultra-Low Cost AKS Cluster

## Quick Setup (5 minutes):

1. **Connect to your cluster:**
```bash
az aks get-credentials --resource-group {rg} --name {cluster_name}
kubectl get nodes
```

2. **Deploy a sample web application:**
```bash
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --type=LoadBalancer
kubectl get services --watch
```

3. **Access your application:**
```bash
# Get external IP (wait for it to be assigned)
kubectl get service nginx
# Visit http://<EXTERNAL-IP>
```

## Cost Optimization Tips:
- 🎯 **100% Spot Instances**: Saving ~70% on compute costs
- 📊 **Auto-scaling**: Scales down to 0 when not used
- 💡 **Development Focus**: Perfect for dev/test workloads
- ⏰ **Schedule**: Consider shutting down overnight (additional 50% savings)

## Next Steps:
1. Deploy your applications with tolerations for spot instances
2. Set up CI/CD with Azure DevOps or GitHub Actions
3. Monitor costs in Azure Cost Management
4. Consider upgrading to reserved instances for production workloads
""",
                tags=["spot-instances", "development", "ultra-cheap", "beginner-friendly"]
            ),
            
            ResourceTemplate(
                id="web-server-ultra-low",
                name="Ultra-Cheap Web Server",
                resource_type="web-server",
                description="Minimal web server setup using Container Instances",
                cost_tier="ultra-low",
                monthly_cost_estimate=15.0,
                configuration={
                    "compute_type": "container_instance",
                    "cpu": 0.5,
                    "memory": "1.0Gi",
                    "os_type": "Linux",
                    "restart_policy": "Always",
                    "enable_log_analytics": True,
                    "public_ip": True
                },
                deployment_time_minutes=3,
                use_cases=["Static websites", "Simple APIs", "Development", "Personal projects"],
                prerequisites=["Resource Group"],
                post_deployment_guide="""
# 🌐 Your Web Server is Ready!

## Quick Start (2 minutes):

1. **Access your web server:**
   - URL: http://{public_ip}
   - Your server is running and accessible!

2. **Deploy your website content:**
```bash
# Option 1: Upload via Azure Storage (Static Content)
az storage blob upload-batch --source ./my-website --destination $web --account-name {storage_account}

# Option 2: Use Docker container (Dynamic Content)
az container create --resource-group {rg} --name my-app --image nginx --ports 80
```

3. **Monitor your web server:**
```bash
# Check container logs
az container logs --resource-group {rg} --name {container_name}

# View metrics
az monitor metrics list --resource {container_id} --metric-names "CpuUsage,MemoryUsage"
```

## 💰 Cost Breakdown:
- **Container Instance**: ~$10/month (0.5 vCPU, 1GB RAM)
- **Data Transfer**: ~$5/month (first 5GB free)
- **Total**: ~$15/month for 24/7 operation

## Optimization Tips:
- 📊 **Auto-shutdown**: Stop container when not needed
- 🎯 **Static Content**: Use Azure Storage for static files ($2/month)
- 🔄 **CDN**: Add Azure CDN for global performance
- 📈 **Scale Up**: Easy upgrade to App Service when ready

## Monitoring:
- View logs in Azure Portal
- Set up alerts for downtime
- Monitor CPU/Memory usage
""",
                tags=["web-server", "ultra-cheap", "container-instance", "beginner"]
            )
        ]
        
        # Low cost templates
        low_cost_templates = [
            ResourceTemplate(
                id="aks-low-cost-prod",
                name="Low-Cost Production AKS",
                resource_type="aks",
                description="Production-ready AKS with cost optimization",
                cost_tier="low",
                monthly_cost_estimate=150.0,
                configuration={
                    "node_count": 2,
                    "vm_size": "Standard_B4ms",
                    "enable_spot_instances": True,
                    "spot_percentage": 70,
                    "enable_autoscaling": True,
                    "min_nodes": 1,
                    "max_nodes": 10,
                    "network_policy": "calico",
                    "enable_private_cluster": True,
                    "enable_monitoring": True
                },
                deployment_time_minutes=15,
                use_cases=["Small production workloads", "Startups", "MVPs"],
                prerequisites=["Resource Group", "Virtual Network", "Log Analytics"],
                post_deployment_guide="""
# 🚀 Production AKS Cluster Ready!

Your low-cost, production-ready Kubernetes cluster is live with:
- ✅ 70% spot instances for cost savings
- ✅ Auto-scaling enabled
- ✅ Private networking for security
- ✅ Monitoring and logging configured

## Quick Deployment Guide:

1. **Connect and verify:**
```bash
az aks get-credentials --resource-group {rg} --name {cluster_name}
kubectl get nodes -o wide
```

2. **Deploy your first application:**
```bash
# Create namespace
kubectl create namespace production

# Deploy sample app with spot tolerance
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      tolerations:
      - key: "kubernetes.azure.com/scalesetpriority"
        operator: "Equal"
        value: "spot"
        effect: "NoSchedule"
      containers:
      - name: web-app
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
EOF
```

3. **Expose your application:**
```bash
kubectl expose deployment web-app --type=LoadBalancer --port=80 --namespace=production
kubectl get services --namespace=production --watch
```

## 💰 Cost Optimization Features:
- **70% Spot Instances**: ~$450/month savings
- **Auto-scaling**: Scales to 0 during low usage
- **Burstable VMs**: Pay for what you use
- **Reserved Capacity**: Available for stable workloads

## 📊 Monitoring Dashboard:
Access your monitoring at:
- Azure Portal: Container Insights
- Grafana: http://{grafana_url} (admin/admin)
- Logs: Azure Log Analytics workspace

## Next Steps:
1. Set up CI/CD pipelines
2. Configure ingress controller
3. Implement GitOps with ArgoCD
4. Set up backup strategies
""",
                tags=["production", "cost-optimized", "spot-instances", "monitoring"]
            )
        ]
        
        # Add all templates
        all_templates = ultra_low_templates + low_cost_templates
        
        for template in all_templates:
            self.add_resource_template(template)
        
        # Add cost optimization data
        cost_data = [
            ("aks", "eastus", "Standard_B2s", 70.0, 40.0, 0.0832, 0.025),
            ("aks", "eastus", "Standard_B4ms", 70.0, 40.0, 0.1664, 0.050),
            ("aks", "westus2", "Standard_B2s", 68.0, 38.0, 0.0832, 0.027),
            ("container_instance", "eastus", "0.5_cpu_1gb", 0.0, 0.0, 0.0025, 0.0025),
            ("web_app", "eastus", "B1", 0.0, 30.0, 0.018, 0.018),
        ]
        
        cursor = self.conn.cursor()
        for data in cost_data:
            cursor.execute("""
                INSERT OR REPLACE INTO cost_optimization 
                (resource_type, region, instance_type, spot_savings_percent, reserved_savings_percent, 
                 current_price_per_hour, spot_price_per_hour, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, data)
        
        self.conn.commit()
        logger.info("Database initialized with templates and cost data")
    
    def find_cheapest_option(self, user_request: str, resource_type: str = None) -> Optional[ResourceTemplate]:
        """Find the cheapest resource option for a user request using vector search"""
        try:
            # Search in vector database
            results = self.resource_collection.query(
                query_texts=[user_request],
                n_results=10,
                where={"resource_type": resource_type} if resource_type else None
            )
            
            if not results['ids'][0]:
                return None
            
            # Get full template data from SQLite and sort by cost
            templates = []
            for template_id in results['ids'][0]:
                template = self.get_resource_template(template_id)
                if template:
                    templates.append(template)
            
            # Sort by cost and prioritize ultra-low/low cost tiers
            def cost_priority(template):
                tier_priority = {"ultra-low": 0, "low": 1, "medium": 2, "high": 3}
                return (tier_priority.get(template.cost_tier, 4), template.monthly_cost_estimate)
            
            templates.sort(key=cost_priority)
            
            return templates[0] if templates else None
            
        except Exception as e:
            logger.error(f"Error finding cheapest option: {e}")
            return None
    
    def add_resource_template(self, template: ResourceTemplate):
        """Add a resource template to both SQLite and vector database"""
        try:
            # Add to SQLite
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO resource_templates 
                (id, name, resource_type, description, cost_tier, monthly_cost_estimate, 
                 configuration, deployment_time_minutes, use_cases, prerequisites, 
                 post_deployment_guide, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template.id, template.name, template.resource_type, template.description,
                template.cost_tier, template.monthly_cost_estimate, 
                json.dumps(template.configuration), template.deployment_time_minutes,
                json.dumps(template.use_cases), json.dumps(template.prerequisites),
                template.post_deployment_guide, json.dumps(template.tags)
            ))
            self.conn.commit()
            
            # Add to vector database
            search_text = f"{template.name} {template.description} {' '.join(template.use_cases)} {' '.join(template.tags)}"
            
            self.resource_collection.upsert(
                ids=[template.id],
                documents=[search_text],
                metadatas=[{
                    "resource_type": template.resource_type,
                    "cost_tier": template.cost_tier,
                    "monthly_cost": template.monthly_cost_estimate
                }]
            )
            
            logger.info(f"Added resource template: {template.name}")
            
        except Exception as e:
            logger.error(f"Error adding resource template: {e}")
    
    def get_resource_template(self, template_id: str) -> Optional[ResourceTemplate]:
        """Get a resource template by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM resource_templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ResourceTemplate(
                id=row['id'],
                name=row['name'],
                resource_type=row['resource_type'],
                description=row['description'],
                cost_tier=row['cost_tier'],
                monthly_cost_estimate=row['monthly_cost_estimate'],
                configuration=json.loads(row['configuration']),
                deployment_time_minutes=row['deployment_time_minutes'],
                use_cases=json.loads(row['use_cases']),
                prerequisites=json.loads(row['prerequisites']),
                post_deployment_guide=row['post_deployment_guide'],
                tags=json.loads(row['tags'])
            )
            
        except Exception as e:
            logger.error(f"Error getting resource template: {e}")
            return None
    
    def get_cost_optimization_data(self, resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Get cost optimization data for a resource type and region"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM cost_optimization 
            WHERE resource_type = ? AND region = ?
            ORDER BY spot_savings_percent DESC
        """, (resource_type, region))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def record_deployment(self, deployment: DeploymentHistory):
        """Record a deployment in history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO deployment_history 
                (id, user_request, resources_created, total_cost, deployment_time, status, user_feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment.id, deployment.user_request, 
                json.dumps(deployment.resources_created),
                deployment.total_cost, deployment.deployment_time,
                deployment.status, deployment.user_feedback
            ))
            self.conn.commit()
            
            # Add to vector search for learning
            self.deployment_collection.upsert(
                ids=[deployment.id],
                documents=[deployment.user_request],
                metadatas=[{
                    "status": deployment.status,
                    "cost": deployment.total_cost,
                    "timestamp": deployment.deployment_time.isoformat()
                }]
            )
            
        except Exception as e:
            logger.error(f"Error recording deployment: {e}")
    
    def get_deployment_history(self, limit: int = 50) -> List[DeploymentHistory]:
        """Get recent deployment history"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM deployment_history 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append(DeploymentHistory(
                id=row['id'],
                user_request=row['user_request'],
                resources_created=json.loads(row['resources_created']),
                total_cost=row['total_cost'],
                deployment_time=datetime.fromisoformat(row['deployment_time']),
                status=row['status'],
                user_feedback=row['user_feedback']
            ))
        
        return history
    
    def learn_from_feedback(self, deployment_id: str, feedback: str, rating: int):
        """Learn from user feedback to improve recommendations"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE deployment_history 
                SET user_feedback = ? 
                WHERE id = ?
            """, (f"{feedback} (Rating: {rating}/5)", deployment_id))
            self.conn.commit()
            
            # Update vector database with feedback
            self.deployment_collection.update(
                ids=[deployment_id],
                metadatas=[{"feedback_rating": rating}]
            )
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
    
    def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics for the dashboard"""
        cursor = self.conn.cursor()
        
        # Most popular resource types
        cursor.execute("""
            SELECT resource_type, COUNT(*) as count 
            FROM deployment_history dh
            JOIN resource_templates rt ON dh.id = rt.id
            WHERE dh.status = 'success'
            GROUP BY resource_type 
            ORDER BY count DESC
            LIMIT 5
        """)
        popular_resources = [dict(row) for row in cursor.fetchall()]
        
        # Average cost by tier
        cursor.execute("""
            SELECT cost_tier, AVG(monthly_cost_estimate) as avg_cost, COUNT(*) as count
            FROM resource_templates 
            GROUP BY cost_tier
        """)
        cost_by_tier = [dict(row) for row in cursor.fetchall()]
        
        # Deployment success rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*) as success_rate,
                COUNT(*) as total_deployments
            FROM deployment_history
            WHERE created_at >= datetime('now', '-30 days')
        """)
        success_stats = dict(cursor.fetchone())
        
        return {
            "popular_resources": popular_resources,
            "cost_by_tier": cost_by_tier,
            "success_rate": success_stats['success_rate'],
            "total_deployments": success_stats['total_deployments']
        }
    
    def close(self):
        """Close database connections"""
        if self.conn:
            self.conn.close()

# Global database instance
_db_instance = None

def get_database() -> IntelligentDatabase:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = IntelligentDatabase()
    return _db_instance