const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const port = 3000;

// Proxy API requests to backend
app.use('/api', createProxyMiddleware({
    target: 'http://localhost:8000',
    changeOrigin: true,
    logLevel: 'info'
}));

// Serve static files
app.use(express.static('public'));

// Main route - AI DevOps Agent UI
app.get('/', (req, res) => {
    res.send(`
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
                        placeholder="e.g., I need Azure Event Grid topic for processing payment events with high availability and security compliance"
                        class="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-200 focus:border-blue-400 resize-none text-lg transition-all duration-200"
                        rows="4">
                    </textarea>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label class="block font-semibold text-gray-700 mb-2">Cloud Provider</label>
                        <select x-model="selectedProvider" class="w-full p-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                            <option value="azure">Microsoft Azure</option>
                            <option value="aws">Amazon AWS</option>
                            <option value="gcp">Google Cloud</option>
                        </select>
                    </div>

                    <div>
                        <label class="block font-semibold text-gray-700 mb-2">Monthly Budget ($)</label>
                        <input 
                            x-model="budgetLimit"
                            type="number" 
                            placeholder="e.g., 1000"
                            class="w-full p-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                    </div>

                    <div>
                        <label class="block font-semibold text-gray-700 mb-2">Security Level</label>
                        <select x-model="securityLevel" class="w-full p-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                            <option value="basic">Basic - Standard protection</option>
                            <option value="standard">Standard - Recommended</option>
                            <option value="high">High - Maximum security</option>
                        </select>
                    </div>
                </div>

                <button 
                    @click="generatePlan()"
                    :disabled="loading || !userRequest.trim()"
                    class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-8 rounded-xl hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 text-lg font-semibold shadow-lg">
                    <span x-show="!loading" class="flex items-center justify-center">
                        <i class="fas fa-rocket mr-3"></i>
                        Generate AI-Powered Infrastructure Plan
                    </span>
                    <span x-show="loading" class="flex items-center justify-center">
                        <i class="fas fa-brain pulse mr-3"></i>
                        AI is analyzing your requirements...
                    </span>
                </button>
            </div>
        </div>

        <!-- Results will appear here -->
        <div x-show="plan" class="bg-white rounded-xl shadow-lg p-8 card-hover">
            <h3 class="text-2xl font-bold mb-6 flex items-center">
                <i class="fas fa-blueprint text-indigo-500 mr-4"></i>
                Your Infrastructure Plan
            </h3>
            <pre class="bg-gray-900 text-green-400 p-6 rounded-xl overflow-x-auto text-sm" x-text="JSON.stringify(plan, null, 2)"></pre>
        </div>
    </div>

    <script>
        function infrastructureApp() {
            return {
                selectedProvider: 'azure',
                userRequest: '',
                budgetLimit: '',
                securityLevel: 'standard',
                loading: false,
                plan: null,
                
                async generatePlan() {
                    if (!this.userRequest.trim()) {
                        alert('Please describe what infrastructure you want to build!');
                        return;
                    }
                    
                    this.loading = true;
                    this.plan = null;
                    
                    try {
                        const response = await fetch('/api/v1/infrastructure/plan', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                user_request: this.userRequest,
                                cloud_provider: this.selectedProvider,
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
                        
                    } catch (error) {
                        console.error('Error generating plan:', error);
                        alert('Failed to generate plan: ' + error.message + '. Please check if the backend is running.');
                    } finally {
                        this.loading = false;
                    }
                }
            }
        }
    </script>
</body>
</html>
    `);
});

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'AI DevOps Agent Frontend',
        framework: 'Express.js',
        timestamp: new Date().toISOString() 
    });
});

app.listen(port, () => {
    console.log('🚀 AI DevOps Agent Frontend running on http://localhost:' + port);
});