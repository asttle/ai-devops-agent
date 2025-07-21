#!/usr/bin/env python3
"""
Enhanced Azure AI DevOps Agent - Streamlit Web Interface with Intelligence
Real-time deployment feedback, cost optimization, and multiple LLM providers
"""

import streamlit as st
import asyncio
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import uuid

# Configure Streamlit page
st.set_page_config(
    page_title="Azure AI DevOps Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our enhanced modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import get_config, validate_environment
    from database import get_database
    from llm import get_llm_manager
    from core import get_intelligent_agent, get_azure_manager
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.stop()

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize all components with caching"""
    try:
        config = get_config()
        database = get_database()
        llm_manager = get_llm_manager()
        intelligent_agent = get_intelligent_agent()
        azure_manager = get_azure_manager()
        
        return {
            'config': config,
            'database': database,
            'llm_manager': llm_manager,
            'intelligent_agent': intelligent_agent,
            'azure_manager': azure_manager,
            'initialized': True
        }
    except Exception as e:
        st.error(f"Failed to initialize components: {e}")
        return {'initialized': False, 'error': str(e)}

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #0078d4, #106ebe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .cost-ultra-low {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .cost-low {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .deployment-progress {
        background-color: #e7f3ff;
        border: 1px solid #0078d4;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .llm-provider-free {
        color: #28a745;
        font-weight: bold;
    }
    
    .llm-provider-paid {
        color: #ffc107;
    }
    
    .resource-guide {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Display enhanced header with LLM provider status"""
    st.markdown('<h1 class="main-header">🚀 Azure AI DevOps Agent</h1>', unsafe_allow_html=True)
    
    # Show current LLM provider
    components = initialize_components()
    if components['initialized']:
        llm_manager = components['llm_manager']
        providers = llm_manager.get_available_providers()
        cheapest = llm_manager.get_cheapest_provider()
        
        if providers:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                provider_info = next((p for p in providers if p["name"] == cheapest), None)
                if provider_info:
                    free_badge = " 🆓 FREE" if provider_info["free"] else f" 💰 ${provider_info['cost_per_1k_input']:.3f}/1K tokens"
                    st.info(f"🤖 AI Provider: **{provider_info['name']}** ({provider_info['model']}){free_badge}")
    
    st.markdown("---")

def show_enhanced_sidebar():
    """Display enhanced sidebar with intelligence features"""
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # Environment validation
        st.subheader("📋 System Status")
        components = initialize_components()
        
        if components['initialized']:
            config = components['config']
            llm_manager = components['llm_manager']
            database = components['database']
            
            # LLM providers status
            providers = llm_manager.get_available_providers()
            st.write("**🤖 AI Providers:**")
            for provider in providers[:3]:  # Show top 3
                free_icon = "🆓" if provider["free"] else "💰"
                st.write(f"{free_icon} {provider['name']} ({provider['model']})")
            
            # Database status
            try:
                analytics = database.get_usage_analytics()
                total_deployments = analytics.get('total_deployments', 0)
                success_rate = analytics.get('success_rate', 0)
                st.write(f"**📊 Analytics:**")
                st.write(f"✅ {total_deployments} deployments")
                st.write(f"📈 {success_rate:.1f}% success rate")
            except:
                st.write("📊 Analytics: Loading...")
            
        else:
            st.error("❌ System initialization failed")
            st.error(components.get('error', 'Unknown error'))
        
        st.divider()
        
        # Cost Insights
        st.subheader("💰 Cost Insights")
        if components['initialized']:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cheapest Option", "$15/mo", help="Ultra-cheap web server")
            with col2:
                st.metric("Avg Savings", "65%", help="With spot instances")
        
        st.divider()
        
        # Quick Actions
        st.subheader("⚡ Quick Deploy")
        if st.button("🌐 Cheap Web Server", help="$15/month"):
            st.session_state.quick_action = "web_server_cheap"
        if st.button("⚙️ Dev AKS Cluster", help="$45/month"):
            st.session_state.quick_action = "aks_ultra_low"
        if st.button("🚀 Production AKS", help="$150/month"):
            st.session_state.quick_action = "aks_production"

def show_intelligent_chat():
    """Display the enhanced chat interface with intelligence"""
    st.header("💬 Intelligent AI Assistant")
    st.write("Tell me what you want to deploy - I'll find the cheapest option and deploy it with real-time progress!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🚀 Hi! I'm your intelligent Azure AI DevOps agent. I can deploy ultra-cheap infrastructure and show you exactly what's happening. What would you like to create?\n\n**Popular options:**\n- \"Create a cheap web server\" ($15/month)\n- \"Create a development AKS cluster\" ($45/month)\n- \"Create a production-ready AKS cluster\" ($150/month)"}
        ]
    
    if "current_deployment" not in st.session_state:
        st.session_state.current_deployment = None
    
    if "deployment_container" not in st.session_state:
        st.session_state.deployment_container = None
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "deployment_plan" in message:
                # Special rendering for deployment plans
                show_deployment_plan(message["deployment_plan"])
            else:
                st.write(message["content"])
    
    # Handle active deployment
    if st.session_state.current_deployment:
        show_real_time_deployment(st.session_state.current_deployment)
    
    # Chat input
    if prompt := st.chat_input("What would you like to deploy?", disabled=bool(st.session_state.current_deployment)):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with Intelligent Agent
        with st.chat_message("assistant"):
            process_intelligent_request(prompt)

def process_intelligent_request(user_input: str):
    """Process user input with the intelligent agent"""
    components = initialize_components()
    if not components['initialized']:
        st.error("System not available. Please check configuration.")
        return
    
    intelligent_agent = components['intelligent_agent']
    
    with st.spinner("🧠 Finding the best solution for you..."):
        try:
            # Process with intelligent agent
            response = asyncio.run(intelligent_agent.process_intelligent_request(
                user_input=user_input,
                prefer_cheapest=True,
                session_id=str(uuid.uuid4())
            ))
            
            if response["action"] == "intelligent_deployment":
                # Show the intelligent plan
                show_intelligent_deployment_plan(response)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["explanation"],
                    "deployment_plan": response,
                    "type": "deployment_plan"
                })
                
            elif response["action"] == "suggestion":
                # Show suggestions
                st.write(response["message"])
                suggestion = response["suggestion"]
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Recommended:** {suggestion['suggested_alternative']}")
                    st.write(f"**Why:** {suggestion['reasoning']}")
                with col2:
                    st.metric("Est. Cost", suggestion['cost_estimate'])
                
                if st.button("✅ Deploy This Instead"):
                    # Trigger deployment of suggested alternative
                    st.session_state.messages.append({"role": "user", "content": suggestion['suggested_alternative']})
                    st.rerun()
            
            else:
                # Default response
                st.write(response.get('message', 'I understand. How can I help you deploy something?'))
                if 'suggestions' in response:
                    for suggestion in response['suggestions']:
                        if st.button(f"💡 {suggestion}"):
                            st.session_state.messages.append({"role": "user", "content": suggestion})
                            st.rerun()
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I encountered an error. Please try again or check your configuration."
            })

def show_intelligent_deployment_plan(plan: Dict[str, Any]):
    """Show intelligent deployment plan with cost optimization"""
    template = plan["template"]
    deployment_plan = plan["deployment_plan"]
    
    # Cost tier styling
    cost_class = "cost-ultra-low" if template.cost_tier == "ultra-low" else "cost-low"
    
    st.markdown(f"""
    <div class="{cost_class}">
        <h3>🎯 {template.name}</h3>
        <p><strong>Cost Tier:</strong> {template.cost_tier.upper()}</p>
        <p><strong>Monthly Cost:</strong> ${template.monthly_cost_estimate}</p>
        <p><strong>Deployment Time:</strong> ~{template.deployment_time_minutes} minutes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show explanation
    st.write("**Why this is perfect for you:**")
    st.write(plan["explanation"])
    
    # Show cost optimizations
    if deployment_plan.get("cost_optimizations"):
        st.write("**💰 Cost Optimizations Included:**")
        for optimization in deployment_plan["cost_optimizations"]:
            st.write(f"• {optimization}")
    
    # Show deployment steps
    with st.expander("🔍 View Detailed Deployment Plan"):
        for step in deployment_plan["steps"]:
            st.write(f"**Step {step['step']}:** {step['name']} (~{step['estimated_minutes']} min)")
            st.progress(0)  # Empty progress bar for preview
    
    # Deployment buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Deploy Now", type="primary", key=f"deploy_{template.id}"):
            start_intelligent_deployment(plan)
    
    with col2:
        if st.button("❌ Cancel", key=f"cancel_{template.id}"):
            st.info("Deployment cancelled")
    
    with col3:
        st.write(f"💡 **Use Cases:** {', '.join(template.use_cases[:2])}")

def start_intelligent_deployment(plan: Dict[str, Any]):
    """Start intelligent deployment with real-time feedback"""
    st.session_state.current_deployment = plan
    st.session_state.deployment_start_time = time.time()
    st.rerun()

def show_real_time_deployment(deployment_plan: Dict[str, Any]):
    """Show real-time deployment progress"""
    template = deployment_plan["template"]
    session_id = deployment_plan["session_id"]
    
    # Create deployment container
    deployment_container = st.empty()
    
    with deployment_container.container():
        st.markdown('<div class="deployment-progress">', unsafe_allow_html=True)
        st.subheader(f"🚀 Deploying {template.name}")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        step_text = st.empty()
        
        # Start the deployment
        components = initialize_components()
        intelligent_agent = components['intelligent_agent']
        
        try:
            # Run the deployment with real-time feedback
            deployment_generator = intelligent_agent.execute_deployment_with_feedback(
                template, session_id
            )
            
            # Process deployment updates
            for update in asyncio.run(consume_deployment_updates(deployment_generator)):
                if update["type"] == "progress":
                    progress_bar.progress(update["progress"] / 100.0)
                    status_text.success(update["message"])
                    step_text.write(f"**Current Step:** {update.get('current_step', 'Processing...')}")
                    time.sleep(0.5)  # Brief delay for visual effect
                
                elif update["type"] == "error":
                    progress_bar.progress(update["progress"] / 100.0)
                    status_text.error(update["message"])
                    st.session_state.current_deployment = None
                    break
                
                elif update["type"] == "success":
                    progress_bar.progress(1.0)
                    status_text.success(update["message"])
                    
                    # Show deployment results
                    show_deployment_success(update)
                    
                    # Clear current deployment
                    st.session_state.current_deployment = None
                    break
        
        except Exception as e:
            status_text.error(f"Deployment failed: {str(e)}")
            st.session_state.current_deployment = None
        
        st.markdown('</div>', unsafe_allow_html=True)

async def consume_deployment_updates(generator):
    """Consume deployment updates from async generator"""
    async for update in generator:
        yield update

def show_deployment_success(success_data: Dict[str, Any]):
    """Show deployment success information and usage guide"""
    st.balloons()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.success(f"🎉 Deployment completed in {success_data.get('duration_minutes', 0)} minutes!")
        st.metric("Total Cost", f"${success_data.get('total_cost', 0):.2f}/month")
        
        # Show created resources
        if success_data.get("resources_created"):
            st.write("**Resources Created:**")
            for resource in success_data["resources_created"]:
                status_icon = "✅" if resource["status"] == "success" else "⏳" if resource["status"] == "exists" else "❌"
                st.write(f"{status_icon} {resource['type']}: {resource['name']}")
    
    with col2:
        st.write("**🎯 What's Next?**")
        st.write("Your personalized usage guide is ready below!")
        
        # Feedback section
        st.write("**Rate this deployment:**")
        rating = st.slider("Rating (1-5 stars)", 1, 5, 5, key="deployment_rating")
        feedback = st.text_input("Feedback (optional)", key="deployment_feedback")
        
        if st.button("Submit Feedback"):
            components = initialize_components()
            intelligent_agent = components['intelligent_agent']
            asyncio.run(intelligent_agent.record_user_feedback(
                success_data["deployment_id"], 
                feedback, 
                rating
            ))
            st.success("Thank you for your feedback!")
    
    # Show personalized usage guide
    if success_data.get("personalized_guide"):
        st.subheader("📖 Your Personalized Usage Guide")
        st.markdown(f'<div class="resource-guide">{success_data["personalized_guide"]}</div>', 
                   unsafe_allow_html=True)

def show_cost_intelligence_dashboard():
    """Show cost intelligence and analytics dashboard"""
    st.header("💰 Cost Intelligence Dashboard")
    
    components = initialize_components()
    if not components['initialized']:
        st.error("Dashboard not available")
        return
    
    intelligent_agent = components['intelligent_agent']
    
    try:
        insights = asyncio.run(intelligent_agent.get_cost_insights())
        
        # Cost overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Potential Monthly Savings", f"${insights['cost_optimization']['potential_monthly_savings']:,.0f}")
        
        with col2:
            st.metric("Average Deployment Cost", f"${insights['cost_optimization']['average_deployment_cost']:.0f}")
        
        with col3:
            st.metric("Cheapest Option", f"${insights['cost_optimization']['cheapest_option_available']:.0f}/mo")
        
        with col4:
            llm_cost = insights['llm_providers']['total_llm_cost_today']
            st.metric("AI Cost Today", f"${llm_cost:.3f}", help="LLM usage costs")
        
        # Usage analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Popular Resources")
            analytics = insights['usage_analytics']
            if analytics.get('popular_resources'):
                df = pd.DataFrame(analytics['popular_resources'])
                fig = px.bar(df, x='resource_type', y='count', title="Most Deployed Resources")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💰 Cost Distribution by Tier")
            if analytics.get('cost_by_tier'):
                df = pd.DataFrame(analytics['cost_by_tier'])
                fig = px.pie(df, values='count', names='cost_tier', title="Deployments by Cost Tier")
                st.plotly_chart(fig, use_container_width=True)
        
        # LLM Provider comparison
        st.subheader("🤖 AI Provider Comparison")
        llm_providers = insights['llm_providers']['available_providers']
        if llm_providers:
            df = pd.DataFrame(llm_providers)
            df['status'] = df['free'].apply(lambda x: '🆓 Free' if x else '💰 Paid')
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.dataframe(df[['name', 'model', 'status', 'cost_per_1k_input']], use_container_width=True)
            with col2:
                current_provider = insights['llm_providers']['current_cheapest']
                st.info(f"**Current Provider:** {current_provider}")
                
                # Show provider switch option
                if st.button("🔄 Switch to Cheapest"):
                    st.success(f"Switched to {current_provider}!")
        
        # Deployment history
        st.subheader("📈 Recent Deployments")
        database = components['database']
        history = database.get_deployment_history(limit=10)
        
        if history:
            history_data = []
            for deployment in history:
                history_data.append({
                    "Time": deployment.deployment_time.strftime("%Y-%m-%d %H:%M"),
                    "Request": deployment.user_request[:50] + "..." if len(deployment.user_request) > 50 else deployment.user_request,
                    "Status": deployment.status,
                    "Cost": f"${deployment.total_cost:.2f}",
                    "Resources": len(deployment.resources_created)
                })
            
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No deployments yet. Start by deploying your first resource!")
    
    except Exception as e:
        st.error(f"Error loading cost insights: {e}")

def handle_quick_actions():
    """Handle quick actions from sidebar"""
    if hasattr(st.session_state, 'quick_action'):
        action = st.session_state.quick_action
        del st.session_state.quick_action
        
        action_map = {
            "web_server_cheap": "Create an ultra-cheap web server for $15/month",
            "aks_ultra_low": "Create a development AKS cluster for $45/month",
            "aks_production": "Create a production-ready AKS cluster for $150/month"
        }
        
        if action in action_map:
            st.session_state.messages.append({"role": "user", "content": action_map[action]})
            st.rerun()

def main():
    """Main application entry point"""
    load_css()
    show_header()
    show_enhanced_sidebar()
    
    # Handle quick actions
    handle_quick_actions()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Intelligent Assistant", "💰 Cost Intelligence", "📊 Analytics"])
    
    with tab1:
        show_intelligent_chat()
    
    with tab2:
        show_cost_intelligence_dashboard()
    
    with tab3:
        st.subheader("📊 System Analytics")
        st.info("Advanced analytics coming soon...")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🚀 Azure AI DevOps Agent v2.0 - Powered by Vector Embeddings & Multiple LLM Providers
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()