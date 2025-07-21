#!/usr/bin/env python3
"""
LLM Providers - Support for multiple LLM providers including free options
Supports Azure OpenAI, Google Gemini Flash 2.0, Ollama, and others
"""

import os
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    usage: Dict[str, int] = None
    model: str = ""
    provider: str = ""
    cost: float = 0.0

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured"""
        pass
    
    @abstractmethod
    def get_cost_per_token(self) -> Dict[str, float]:
        """Get cost per input/output token"""
        pass

class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    
    def is_available(self) -> bool:
        return bool(self.endpoint and self.api_key)
    
    def get_cost_per_token(self) -> Dict[str, float]:
        # GPT-4 pricing (approximate)
        return {"input": 0.00003, "output": 0.00006}
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        if not self.is_available():
            raise ValueError("Azure OpenAI not configured")
        
        try:
            import openai
            
            client = openai.AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
            
            response = client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 1500),
                response_format=kwargs.get("response_format", {"type": "text"})
            )
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            costs = self.get_cost_per_token()
            total_cost = (usage["prompt_tokens"] * costs["input"] + 
                         usage["completion_tokens"] * costs["output"])
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.deployment_name,
                provider="azure_openai",
                cost=total_cost
            )
            
        except Exception as e:
            logger.error(f"Azure OpenAI error: {e}")
            raise

class GoogleGeminiProvider(BaseLLMProvider):
    """Google Gemini Flash 2.0 provider (free tier available)"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        self.model_name = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_cost_per_token(self) -> Dict[str, float]:
        # Gemini Flash is free up to certain limits
        return {"input": 0.0, "output": 0.0}  # Free tier
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        if not self.is_available():
            raise ValueError("Google Gemini not configured")
        
        try:
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.1),
                    "maxOutputTokens": kwargs.get("max_tokens", 1500),
                    "candidateCount": 1
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.model_name}:generateContent",
                    params={"key": self.api_key},
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                response.raise_for_status()
                
            data = response.json()
            
            if "candidates" not in data or not data["candidates"]:
                raise ValueError("No response from Gemini")
            
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Extract usage info if available
            usage = {}
            if "usageMetadata" in data:
                metadata = data["usageMetadata"]
                usage = {
                    "prompt_tokens": metadata.get("promptTokenCount", 0),
                    "completion_tokens": metadata.get("candidatesTokenCount", 0),
                    "total_tokens": metadata.get("totalTokenCount", 0)
                }
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.model_name,
                provider="google_gemini",
                cost=0.0  # Free tier
            )
            
        except Exception as e:
            logger.error(f"Google Gemini error: {e}")
            raise

class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLMs"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    def is_available(self) -> bool:
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/version", timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    def get_cost_per_token(self) -> Dict[str, float]:
        return {"input": 0.0, "output": 0.0}  # Local, free
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        if not self.is_available():
            raise ValueError("Ollama not available")
        
        try:
            # Convert to Ollama chat format
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.1),
                    "num_predict": kwargs.get("max_tokens", 1500)
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                
            data = response.json()
            content = data["message"]["content"]
            
            return LLMResponse(
                content=content,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                model=self.model_name,
                provider="ollama",
                cost=0.0
            )
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise

class GroqProvider(BaseLLMProvider):
    """Groq provider for fast inference (has free tier)"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.base_url = "https://api.groq.com/openai/v1"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_cost_per_token(self) -> Dict[str, float]:
        # Groq pricing (very cheap)
        return {"input": 0.00000018, "output": 0.00000018}
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        if not self.is_available():
            raise ValueError("Groq not configured")
        
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.1),
                "max_tokens": kwargs.get("max_tokens", 1500),
                "stream": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            usage = data.get("usage", {})
            costs = self.get_cost_per_token()
            total_cost = (usage.get("prompt_tokens", 0) * costs["input"] + 
                         usage.get("completion_tokens", 0) * costs["output"])
            
            return LLMResponse(
                content=content,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                model=self.model_name,
                provider="groq",
                cost=total_cost
            )
            
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter gateway provider - Access to multiple LLMs through one API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_name = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku:beta")
        self.base_url = "https://openrouter.ai/api/v1"
        self.app_name = os.getenv("OPENROUTER_APP_NAME", "Azure AI DevOps Agent")
        self.site_url = os.getenv("OPENROUTER_SITE_URL", "https://github.com/azure-ai-devops-agent")
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_cost_per_token(self) -> Dict[str, float]:
        # OpenRouter pricing varies by model, these are approximate for Claude Haiku
        model_costs = {
            "anthropic/claude-3-haiku:beta": {"input": 0.00025, "output": 0.00125},
            "openai/gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "openai/gpt-4": {"input": 0.03, "output": 0.06},
            "meta-llama/llama-3.1-8b-instruct:free": {"input": 0.0, "output": 0.0},
            "google/gemini-flash-1.5": {"input": 0.000075, "output": 0.0003},
        }
        return model_costs.get(self.model_name, {"input": 0.001, "output": 0.002})
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        if not self.is_available():
            raise ValueError("OpenRouter not configured")
        
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.1),
                "max_tokens": kwargs.get("max_tokens", 1500),
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.app_name
            }
            
            # Handle JSON response format for OpenAI-compatible models
            if kwargs.get("response_format", {}).get("type") == "json_object":
                payload["response_format"] = {"type": "json_object"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                raise ValueError(f"OpenRouter error: {data['error']['message']}")
            
            content = data["choices"][0]["message"]["content"]
            
            usage = data.get("usage", {})
            costs = self.get_cost_per_token()
            total_cost = (usage.get("prompt_tokens", 0) * costs["input"] + 
                         usage.get("completion_tokens", 0) * costs["output"])
            
            return LLMResponse(
                content=content,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                model=self.model_name,
                provider="openrouter",
                cost=total_cost
            )
            
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            raise

class LLMManager:
    """Manages multiple LLM providers with fallbacks"""
    
    def __init__(self):
        self.providers = {
            "azure_openai": AzureOpenAIProvider(),
            "google_gemini": GoogleGeminiProvider(),
            "openrouter": OpenRouterProvider(),
            "groq": GroqProvider(),
            "ollama": OllamaProvider()
        }
        
        self.fallback_order = self._determine_fallback_order()
        logger.info(f"Available LLM providers: {[name for name, provider in self.providers.items() if provider.is_available()]}")
    
    def _determine_fallback_order(self) -> List[str]:
        """Determine the best fallback order based on availability and cost"""
        available = [(name, provider) for name, provider in self.providers.items() if provider.is_available()]
        
        # Prioritize free providers first, then by cost and reliability
        priority_order = ["google_gemini", "ollama", "openrouter", "groq", "azure_openai"]
        
        ordered = []
        for provider_name in priority_order:
            if any(name == provider_name for name, _ in available):
                ordered.append(provider_name)
        
        return ordered
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              preferred_provider: str = None, **kwargs) -> LLMResponse:
        """Generate response using preferred provider with fallbacks"""
        
        providers_to_try = [preferred_provider] if preferred_provider else []
        providers_to_try.extend(self.fallback_order)
        
        last_error = None
        
        for provider_name in providers_to_try:
            if not provider_name or provider_name not in self.providers:
                continue
                
            provider = self.providers[provider_name]
            if not provider.is_available():
                continue
            
            try:
                logger.info(f"Attempting to use LLM provider: {provider_name}")
                response = await provider.generate_response(messages, **kwargs)
                logger.info(f"Successfully used {provider_name}, cost: ${response.cost:.4f}")
                return response
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                last_error = e
                continue
        
        # No providers worked
        raise Exception(f"All LLM providers failed. Last error: {last_error}")
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their details"""
        result = []
        for name, provider in self.providers.items():
            if provider.is_available():
                costs = provider.get_cost_per_token()
                result.append({
                    "name": name,
                    "model": getattr(provider, 'model_name', 'unknown'),
                    "cost_per_1k_input": costs["input"] * 1000,
                    "cost_per_1k_output": costs["output"] * 1000,
                    "free": costs["input"] == 0 and costs["output"] == 0
                })
        return result
    
    def get_cheapest_provider(self) -> str:
        """Get the cheapest available provider"""
        available = self.get_available_providers()
        if not available:
            return None
        
        # Prioritize free providers
        free_providers = [p for p in available if p["free"]]
        if free_providers:
            return free_providers[0]["name"]
        
        # Otherwise, find cheapest
        cheapest = min(available, key=lambda x: x["cost_per_1k_input"] + x["cost_per_1k_output"])
        return cheapest["name"]

# Global LLM manager instance
_llm_manager = None

def get_llm_manager() -> LLMManager:
    """Get the global LLM manager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager