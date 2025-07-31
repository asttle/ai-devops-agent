import { Hono } from 'hono'
import { serve } from '@hono/node-server'
import { serveStatic } from '@hono/node-server/serve-static'

const app = new Hono()

// Serve static files
app.use('/static/*', serveStatic({ root: './public' }))

// API proxy to backend
app.all('/api/*', async (c) => {
  const url = new URL(c.req.url)
  const backendUrl = `http://localhost:8000${url.pathname}${url.search}`
  
  try {
    const response = await fetch(backendUrl, {
      method: c.req.method,
      headers: c.req.header(),
      body: c.req.method !== 'GET' && c.req.method !== 'HEAD' ? await c.req.text() : undefined,
    })
    
    const data = await response.text()
    
    return new Response(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      }
    })
  } catch (error) {
    return c.json({ error: 'Backend service unavailable' }, 503)
  }
})

// Main UI route - AI DevOps Agent
app.get('/', (c) => {
  return c.html(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI DevOps Agent - Cloud Infrastructure Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-hover { transition: all 0.3s ease; }
        .card-hover:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div x-data="infrastructureApp()" class="container mx-auto px-4 py-8 max-w-7xl">
        <!-- Header -->
        <div class="text-center mb-8">
            <div class="gradient-bg rounded-2xl p-8 text-white mb-6">
                <h1 class="text-5xl font-bold mb-2">
                    <i class="fas fa-robot mr-3"></i>
                    AI DevOps Agent
                </h1>
                <p class="text-xl opacity-90 mb-4">Intelligent Cloud Infrastructure Assistant</p>
                <div class="flex justify-center space-x-6 text-sm">
                    <div class="flex items-center">
                        <i class="fas fa-brain mr-2"></i>
                        Pydantic AI
                    </div>
                    <div class="flex items-center">
                        <i class="fas fa-search mr-2"></i>
                        Context7 MCP
                    </div>
                    <div class="flex items-center">
                        <i class="fas fa-cloud mr-2"></i>
                        Multi-Cloud
                    </div>
                    <div class="flex items-center">
                        <i class="fas fa-zap mr-2"></i>
                        Real-time Docs
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-lg p-4 text-center card-hover">
                <i class="fas fa-server text-blue-500 text-2xl mb-2"></i>
                <div class="text-2xl font-bold text-gray-800">3</div>
                <div class="text-sm text-gray-600">Cloud Providers</div>
            </div>
            <div class="bg-white rounded-lg p-4 text-center card-hover">
                <i class="fas fa-dollar-sign text-green-500 text-2xl mb-2"></i>
                <div class="text-2xl font-bold text-gray-800">70%</div>
                <div class="text-sm text-gray-600">Cost Savings</div>
            </div>
            <div class="bg-white rounded-lg p-4 text-center card-hover">
                <i class="fas fa-shield-alt text-purple-500 text-2xl mb-2"></i>
                <div class="text-2xl font-bold text-gray-800">100%</div>
                <div class="text-sm text-gray-600">Security Focus</div>
            </div>
            <div class="bg-white rounded-lg p-4 text-center card-hover">
                <i class="fas fa-clock text-orange-500 text-2xl mb-2"></i>
                <div class="text-2xl font-bold text-gray-800">5min</div>
                <div class="text-sm text-gray-600">Avg Deploy Time</div>
            </div>
        </div>

        <!-- Cloud Provider Selection -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8 card-hover">
            <h2 class="text-2xl font-bold mb-6 flex items-center">
                <i class="fas fa-cloud text-blue-500 mr-3"></i>
                Choose Your Cloud Provider
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <button 
                    @click="selectedProvider = 'aws'"
                    :class="selectedProvider === 'aws' 
                        ? 'bg-gradient-to-r from-orange-400 to-orange-600 text-white shadow-lg transform scale-105' 
                        : 'bg-gray-50 text-gray-700 hover:bg-orange-50'"
                    class="p-6 rounded-xl transition-all duration-300 border-2 card-hover relative">
                    <div class="absolute top-2 right-2 bg-yellow-500 text-white text-xs px-2 py-1 rounded">PLAN ONLY</div>
                    <i class="fab fa-aws text-4xl mb-4"></i>
                    <div class="font-bold text-lg">Amazon AWS</div>
                    <div class="text-sm opacity-80 mt-2">Planning only - no deployment creds</div>
                </button>
                
                <button 
                    @click="selectedProvider = 'azure'"
                    :class="selectedProvider === 'azure' 
                        ? 'bg-gradient-to-r from-blue-400 to-blue-600 text-white shadow-lg transform scale-105' 
                        : 'bg-gray-50 text-gray-700 hover:bg-blue-50'"
                    class="p-6 rounded-xl transition-all duration-300 border-2 card-hover relative">
                    <div class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded">FULL ACCESS</div>
                    <i class="fab fa-microsoft text-4xl mb-4"></i>
                    <div class="font-bold text-lg">Microsoft Azure</div>
                    <div class="text-sm opacity-80 mt-2">Complete deployment & management</div>
                </button>
                
                <button 
                    @click="selectedProvider = 'gcp'"
                    :class="selectedProvider === 'gcp' 
                        ? 'bg-gradient-to-r from-red-400 to-red-600 text-white shadow-lg transform scale-105' 
                        : 'bg-gray-50 text-gray-700 hover:bg-red-50'"
                    class="p-6 rounded-xl transition-all duration-300 border-2 card-hover relative">
                    <div class="absolute top-2 right-2 bg-yellow-500 text-white text-xs px-2 py-1 rounded">PLAN ONLY</div>
                    <i class="fab fa-google text-4xl mb-4"></i>
                    <div class="font-bold text-lg">Google Cloud</div>
                    <div class="text-sm opacity-80 mt-2">Planning only - using Gemini API</div>
                </button>
            </div>
        </div>

        <!-- Infrastructure Request Form -->
        <div class="bg-white rounded-xl shadow-lg p-8 mb-8 card-hover">
            <h2 class="text-2xl font-bold mb-6 flex items-center">
                <i class="fas fa-magic text-purple-500 mr-3"></i>
                Describe Your Infrastructure Vision
            </h2>
            
            <div class="space-y-6">
                <div>
                    <label class="block text-lg font-semibold text-gray-700 mb-3">
                        What infrastructure do you want to build?
                    </label>
                    <textarea
                        x-model="userRequest"
                        placeholder="e.g., I need Azure Event Grid topic for processing payment events with high availability, security compliance, and real-time monitoring. Include proper networking, encryption, and access controls."
                        class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-200 focus:border-blue-400 resize-none text-lg transition-all duration-200"
                        rows="5">
                    </textarea>
                    <div class="text-sm text-gray-500 mt-2 flex items-center">
                        <i class="fas fa-lightbulb mr-2"></i>
                        The more specific you are, the better Context7 MCP can find the latest Terraform attributes!
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label class="block font-semibold text-gray-700 mb-2">Preferred Region</label>
                        <select x-model="region" class="w-full p-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                            <option value="">🌍 Auto-select optimal region</option>
                            <option value="us-east-1">🇺🇸 US East (Virginia)</option>
                            <option value="us-west-2">🇺🇸 US West (Oregon)</option>
                            <option value="eu-west-1">🇪🇺 Europe (Ireland)</option>
                            <option value="ap-southeast-1">🌏 Asia Pacific (Singapore)</option>
                            <option value="ap-northeast-1">🇯🇵 Asia Pacific (Tokyo)</option>
                        </select>
                    </div>

                    <div>
                        <label class="block font-semibold text-gray-700 mb-2">Monthly Budget ($)</label>
                        <input 
                            x-model="budgetLimit"
                            type="number" 
                            placeholder="e.g., 1000"
                            class="w-full p-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                        <div class="text-xs text-gray-500 mt-1">Leave empty for no limit</div>
                    </div>

                    <div>
                        <label class="block font-semibold text-gray-700 mb-2">Security Level</label>
                        <select x-model="securityLevel" class="w-full p-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                            <option value="basic">🔓 Basic - Standard protection</option>
                            <option value="standard">🛡️ Standard - Recommended</option>
                            <option value="high">🔒 High - Maximum security</option>
                        </select>
                    </div>
                </div>

                <button 
                    @click="generatePlan()"
                    :disabled="loading || !userRequest.trim()"
                    class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-8 rounded-xl hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 text-lg font-semibold shadow-lg">
                    <span x-show="!loading" class="flex items-center justify-center">
                        <i class="fas fa-rocket mr-3"></i>
                        Generate AI-Powered Infrastructure Plan (with Context7 MCP)
                    </span>
                    <span x-show="loading" class="flex items-center justify-center">
                        <i class="fas fa-brain pulse mr-3"></i>
                        AI is analyzing with latest docs via Context7 MCP...
                    </span>
                </button>
            </div>
        </div>

        <!-- Quick Examples for Context7 MCP Testing -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8 card-hover" x-show="!plan">
            <h3 class="text-xl font-bold mb-6 flex items-center">
                <i class="fas fa-lightbulb text-yellow-500 mr-3"></i>
                💡 Test Context7 MCP with Latest Azure Features
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button 
                    @click="setExample('event-grid')"
                    class="text-left p-5 border-2 border-gray-100 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 card-hover">
                    <div class="flex items-center mb-2">
                        <i class="fas fa-bolt text-blue-500 mr-3 text-xl"></i>
                        <div class="font-bold text-blue-600 text-lg">Azure Event Grid Topic</div>
                    </div>
                    <div class="text-gray-600">Latest Event Grid with advanced filtering, dead letter queues, and monitoring</div>
                </button>
                
                <button 
                    @click="setExample('aks-advanced')"
                    class="text-left p-5 border-2 border-gray-100 rounded-xl hover:border-green-300 hover:bg-green-50 transition-all duration-200 card-hover">
                    <div class="flex items-center mb-2">
                        <i class="fas fa-dharmachakra text-green-500 mr-3 text-xl"></i>
                        <div class="font-bold text-green-600 text-lg">AKS with Latest Features</div>
                    </div>
                    <div class="text-gray-600">2025 AKS features: Workload Identity, OIDC, Istio service mesh</div>
                </button>
                
                <button 
                    @click="setExample('ai-services')"
                    class="text-left p-5 border-2 border-gray-100 rounded-xl hover:border-purple-300 hover:bg-purple-50 transition-all duration-200 card-hover">
                    <div class="flex items-center mb-2">
                        <i class="fas fa-brain text-purple-500 mr-3 text-xl"></i>
                        <div class="font-bold text-purple-600 text-lg">Azure AI Services Platform</div>
                    </div>
                    <div class="text-gray-600">Latest Azure OpenAI, Cognitive Services, AI Search integration</div>
                </button>
                
                <button 
                    @click="setExample('security-suite')"
                    class="text-left p-5 border-2 border-gray-100 rounded-xl hover:border-orange-300 hover:bg-orange-50 transition-all duration-200 card-hover">
                    <div class="flex items-center mb-2">
                        <i class="fas fa-shield-alt text-orange-500 mr-3 text-xl"></i>
                        <div class="font-bold text-orange-600 text-lg">Zero-Trust Security Suite</div>
                    </div>
                    <div class="text-gray-600">Latest security features: Microsoft Defender, Sentinel, Key Vault</div>
                </button>
            </div>
        </div>

        <!-- Infrastructure Plan Results -->
        <div x-show="plan" class="space-y-8">
            <!-- Plan Overview -->
            <div class="bg-white rounded-xl shadow-lg p-8 card-hover">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-3xl font-bold flex items-center">
                        <i class="fas fa-blueprint text-indigo-500 mr-4"></i>
                        Your Infrastructure Plan
                    </h2>
                    <div class="flex items-center space-x-2 text-green-600">
                        <i class="fas fa-check-circle"></i>
                        <span class="font-semibold">AI Generated with Latest Docs</span>
                    </div>
                </div>
                
                <!-- Key Metrics -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="bg-gradient-to-r from-green-400 to-green-600 p-6 rounded-xl text-white text-center">
                        <i class="fas fa-dollar-sign text-3xl mb-2"></i>
                        <div class="text-sm font-medium opacity-90">Monthly Cost</div>
                        <div class="text-3xl font-bold" x-text="'$' + (plan?.estimated_cost_monthly || 0)"></div>
                    </div>
                    <div class="bg-gradient-to-r from-blue-400 to-blue-600 p-6 rounded-xl text-white text-center">
                        <i class="fas fa-clock text-3xl mb-2"></i>
                        <div class="text-sm font-medium opacity-90">Deploy Time</div>
                        <div class="text-3xl font-bold" x-text="(plan?.estimated_time_minutes || 0) + ' min'"></div>
                    </div>
                    <div class="bg-gradient-to-r from-purple-400 to-purple-600 p-6 rounded-xl text-white text-center">
                        <i class="fas fa-server text-3xl mb-2"></i>
                        <div class="text-sm font-medium opacity-90">Resources</div>
                        <div class="text-3xl font-bold" x-text="(plan?.resources?.length || 0)"></div>
                    </div>
                    <div class="bg-gradient-to-r from-orange-400 to-orange-600 p-6 rounded-xl text-white text-center">
                        <i class="fas fa-cloud text-3xl mb-2"></i>
                        <div class="text-sm font-medium opacity-90">Provider</div>
                        <div class="text-2xl font-bold uppercase" x-text="plan?.cloud_provider || ''"></div>
                    </div>
                </div>

                <!-- Terraform Code with Context7 MCP Indicator -->
                <div class="mb-8" x-show="plan?.terraform_code">
                    <h3 class="text-xl font-bold mb-4 flex items-center">
                        <i class="fas fa-code text-gray-600 mr-3"></i>
                        🚀 Infrastructure as Code (Latest Terraform Attributes via Context7 MCP)
                    </h3>
                    <div class="relative">
                        <pre class="bg-gray-900 text-green-400 p-6 rounded-xl overflow-x-auto text-sm border"><code x-text="plan?.terraform_code || ''"></code></pre>
                        <button 
                            @click="copyToClipboard(plan?.terraform_code || '')"
                            class="absolute top-4 right-4 bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm transition-colors">
                            <i class="fas fa-copy mr-2"></i>Copy Code
                        </button>
                    </div>
                </div>

                <!-- Security Recommendations -->
                <div class="mb-8">
                    <h3 class="text-xl font-bold mb-4 flex items-center">
                        <i class="fas fa-shield-alt text-green-500 mr-3"></i>
                        🛡️ Security & Best Practices
                    </h3>
                    <div class="grid gap-3">
                        <template x-for="(recommendation, index) in plan?.security_recommendations || []" :key="index">
                            <div class="flex items-start p-3 bg-green-50 rounded-lg border-l-4 border-green-400">
                                <i class="fas fa-check-circle text-green-500 mt-1 mr-3"></i>
                                <span class="text-gray-700" x-text="recommendation"></span>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="flex flex-wrap gap-4">
                    <button 
                        @click="deployInfrastructure()"
                        :disabled="deploying"
                        class="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-8 py-3 rounded-xl disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 font-semibold shadow-lg">
                        <span x-show="!deploying" class="flex items-center">
                            <i class="fas fa-rocket mr-3"></i>
                            Deploy to Cloud
                        </span>
                        <span x-show="deploying" class="flex items-center">
                            <i class="fas fa-spinner fa-spin mr-3"></i>
                            Deploying Resources...
                        </span>
                    </button>
                    
                    <button 
                        @click="downloadTerraform()"
                        class="bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 text-white px-8 py-3 rounded-xl transition-all duration-300 transform hover:scale-105 font-semibold shadow-lg">
                        <i class="fas fa-download mr-3"></i>
                        Download Terraform
                    </button>
                    
                    <button 
                        @click="generateNewPlan()"
                        class="bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white px-8 py-3 rounded-xl transition-all duration-300 transform hover:scale-105 font-semibold shadow-lg">
                        <i class="fas fa-redo mr-3"></i>
                        New Plan
                    </button>
                </div>
            </div>

            <!-- Deployment Status -->
            <div x-show="deploymentResult" class="bg-white rounded-xl shadow-lg p-8 card-hover">
                <h3 class="text-2xl font-bold mb-6 flex items-center">
                    <i class="fas fa-tasks text-orange-500 mr-3"></i>
                    🚀 Deployment Status
                </h3>
                
                <div x-show="deploymentResult?.status === 'success'" class="bg-green-50 border-2 border-green-200 rounded-xl p-6">
                    <div class="flex items-center">
                        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mr-4">
                            <i class="fas fa-check-circle text-green-500 text-2xl"></i>
                        </div>
                        <div>
                            <div class="font-bold text-green-800 text-xl">🎉 Deployment Successful!</div>
                            <div class="text-green-700">Your infrastructure has been deployed using the latest Terraform attributes.</div>
                        </div>
                    </div>
                </div>

                <div x-show="deploymentResult?.status === 'failed'" class="bg-red-50 border-2 border-red-200 rounded-xl p-6">
                    <div class="flex items-center">
                        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mr-4">
                            <i class="fas fa-exclamation-triangle text-red-500 text-2xl"></i>
                        </div>
                        <div>
                            <div class="font-bold text-red-800 text-xl">❌ Deployment Failed</div>
                            <div class="text-red-700" x-text="deploymentResult?.error || 'An unknown error occurred during deployment'"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center mt-16 py-8 border-t border-gray-200">
            <div class="text-gray-600 mb-4">
                <p class="text-lg font-semibold">🤖 AI DevOps Agent v2.0 - Enhanced with Context7 MCP</p>
                <p>Powered by Pydantic AI • Context7 MCP • Hono Framework • Latest Cloud Documentation</p>
            </div>
            <div class="flex justify-center space-x-6 text-sm">
                <a href="/api/docs" target="_blank" class="text-blue-500 hover:text-blue-700 flex items-center">
                    <i class="fas fa-book mr-2"></i>API Documentation
                </a>
                <a href="/health" target="_blank" class="text-blue-500 hover:text-blue-700 flex items-center">
                    <i class="fas fa-heartbeat mr-2"></i>Health Check
                </a>
                <span class="text-gray-400">Real-time cloud documentation via Context7 MCP</span>
            </div>
        </div>
    </div>

    <script>
        function infrastructureApp() {
            return {
                selectedProvider: 'azure',
                userRequest: '',
                region: '',
                budgetLimit: '',
                securityLevel: 'standard',
                loading: false,
                deploying: false,
                plan: null,
                deploymentResult: null,
                
                async generatePlan() {
                    if (!this.userRequest.trim()) {
                        alert('Please describe what infrastructure you want to build!');
                        return;
                    }
                    
                    this.loading = true;
                    this.plan = null;
                    this.deploymentResult = null;
                    
                    try {
                        const response = await fetch('/api/v1/infrastructure/plan', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                user_request: this.userRequest,
                                cloud_provider: this.selectedProvider,
                                region: this.region || null,
                                budget_limit: this.budgetLimit ? parseFloat(this.budgetLimit) : null,
                                security_level: this.securityLevel
                            })
                        });
                        
                        if (!response.ok) {
                            const errorData = await response.json().catch(() => ({}));
                            throw new Error(errorData.detail || 'HTTP error! status: ' + response.status);
                        }
                        
                        const data = await response.json();
                        this.plan = data;
                        
                        // Smooth scroll to results
                        setTimeout(() => {
                            document.querySelector('[x-show="plan"]')?.scrollIntoView({ 
                                behavior: 'smooth',
                                block: 'start'
                            });
                        }, 100);
                        
                    } catch (error) {
                        console.error('Error generating plan:', error);
                        alert('Failed to generate plan: ' + error.message + '. Please check if the backend is running.');
                    } finally {
                        this.loading = false;
                    }
                },
                
                async deployInfrastructure() {
                    if (!this.plan) return;
                    
                    this.deploying = true;
                    this.deploymentResult = null;
                    
                    try {
                        const response = await fetch('/api/v1/infrastructure/deploy', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                plan: this.plan,
                                execute_async: false
                            })
                        });
                        
                        if (!response.ok) {
                            const errorData = await response.json().catch(() => ({}));
                            throw new Error(errorData.detail || 'HTTP error! status: ' + response.status);
                        }
                        
                        const data = await response.json();
                        this.deploymentResult = data;
                        
                    } catch (error) {
                        console.error('Error deploying infrastructure:', error);
                        this.deploymentResult = {
                            status: 'failed',
                            error: 'Deployment failed: ' + error.message
                        };
                    } finally {
                        this.deploying = false;
                    }
                },
                
                generateNewPlan() {
                    this.plan = null;
                    this.deploymentResult = null;
                    this.userRequest = '';
                    
                    // Scroll back to top
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                },
                
                downloadTerraform() {
                    if (!this.plan?.terraform_code) {
                        alert('No Terraform code available to download');
                        return;
                    }
                    
                    const blob = new Blob([this.plan.terraform_code], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'infrastructure-' + this.selectedProvider + '-' + Date.now() + '.tf';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    
                    // Show success message
                    alert('🎉 Terraform code downloaded successfully!');
                },
                
                copyToClipboard(text) {
                    if (!text) return;
                    
                    navigator.clipboard.writeText(text).then(() => {
                        alert('📋 Code copied to clipboard!');
                    }).catch(err => {
                        console.error('Failed to copy:', err);
                        alert('Failed to copy code. Please select and copy manually.');
                    });
                },
                
                setExample(type) {
                    const examples = {
                        'event-grid': 'I need to create an Azure Event Grid topic for processing payment events in a production environment. Requirements: high availability across multiple regions, advanced message filtering capabilities, dead letter queue for failed deliveries, integration with Azure Monitor for comprehensive logging and alerting, secure authentication using managed identity, encryption in transit and at rest, network security with private endpoints, proper RBAC setup, and cost optimization with appropriate scaling. The solution should be SOC2 compliant and handle up to 10,000 events per second during peak traffic.',
                        
                        'aks-advanced': 'Create a production-ready Azure Kubernetes Service (AKS) cluster with the latest 2025 features. Requirements: Workload Identity integration for secure pod authentication, OIDC issuer configuration, Istio service mesh for advanced traffic management and security, Azure CNI with network policies, auto-scaling from 3 to 50 nodes using spot instances for cost optimization, Azure Key Vault CSI driver integration, Azure Monitor Container Insights, Azure Defender for Kubernetes security scanning, and automated certificate management. Include proper node pool configuration with dedicated system and user pools, and integrate with Azure DevOps for CI/CD deployments.',
                        
                        'ai-services': 'Build a comprehensive Azure AI services platform for a SaaS application. Requirements: Azure OpenAI service with GPT-4 and embeddings models, Azure Cognitive Services for text analytics and computer vision, Azure AI Search with vector search capabilities, Azure Machine Learning workspace for model training and deployment, proper API management with rate limiting and authentication, integration with Azure Monitor for usage tracking and performance monitoring, secure networking with private endpoints, automated scaling based on demand, and comprehensive logging for compliance and auditing. Include proper cost management with budget alerts and resource optimization recommendations.',
                        
                        'security-suite': 'Implement a complete zero-trust security suite for an enterprise environment. Requirements: Microsoft Defender for Cloud advanced security monitoring, Azure Sentinel SIEM with automated incident response, Azure Key Vault with HSM protection for sensitive secrets, Azure Private DNS zones for secure name resolution, Azure Firewall with application and network rules, Azure DDoS Protection for public-facing resources, Azure Security Center continuous compliance monitoring, proper identity and access management with conditional access policies, comprehensive audit logging with long-term retention, and integration with third-party security tools. The solution should meet SOC2, ISO 27001, and PCI-DSS compliance requirements.'
                    };
                    
                    this.userRequest = examples[type] || '';
                    
                    // Auto-scroll to the text area
                    setTimeout(() => {
                        document.querySelector('textarea').focus();
                        document.querySelector('textarea').scrollIntoView({ 
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 100);
                }
            }
        }
        
        // Add some UI enhancements
        document.addEventListener('DOMContentLoaded', function() {
            // Add loading animation to page
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease-in-out';
            
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);
        });
    </script>
</body>
</html>
  `)
})

// Health check
app.get('/health', (c) => {
  return c.json({ 
    status: 'healthy', 
    service: 'AI DevOps Agent Frontend',
    framework: 'Hono v4.x',
    features: ['Context7 MCP Integration', 'Real-time Documentation', 'Security Validation'],
    timestamp: new Date().toISOString() 
  })
})

const port = 3001
console.log(`🚀 AI DevOps Agent Frontend running on http://localhost:${port}`)
serve({
  fetch: app.fetch,
  port
})