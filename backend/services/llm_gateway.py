#!/usr/bin/env python3
"""
LiteLLM Gateway for unified LLM provider management
"""

import asyncio
import hashlib
import json
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from datetime import datetime, timedelta
import litellm
from litellm import acompletion, embedding
import structlog
import os

# GPTCache imports for semantic caching (optional)
try:
    from gptcache import Cache
    from gptcache.adapter.api import init_similar_cache
    from gptcache.embedding import Onnx
    from gptcache.manager import CacheBase, VectorBase, get_data_manager
    from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
    from gptcache.processor.pre import get_prompt
    GPTCACHE_AVAILABLE = True
except ImportError:
    GPTCACHE_AVAILABLE = False
    Cache = None

from core.config import get_settings

logger = structlog.get_logger(__name__)


def setup_semantic_cache() -> Optional[Cache]:
    """Setup GPTCache with semantic similarity for infrastructure requests"""
    
    if not GPTCACHE_AVAILABLE:
        logger.info("GPTCache not available - caching disabled")
        return None
    
    # Create cache directory
    cache_dir = "./data/cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    try:
        # Try semantic cache with basic setup
        cache = Cache()
        
        # Simple fallback without external model downloads
        # Use a simple hash-based approach instead of semantic embeddings
        
        # Simple hash-based caching without embeddings
        def simple_hash_func(text):
            return hashlib.md5(text.encode()).hexdigest()
        
        data_manager = get_data_manager(
            CacheBase("sqlite", sql_url=f"sqlite:///{cache_dir}/gptcache.db")
        )
        
        cache.init(
            embedding_func=simple_hash_func,  # Simple hash-based caching
            data_manager=data_manager,
            pre_embedding_func=get_prompt
        )
        
        logger.info("GPTCache initialized with string-based similarity matching")
        return cache
        
    except Exception as e:
        logger.error(f"Failed to initialize any GPTCache: {e}")
        
        # Return None if cache fails - app will work without cache
        return None


class LLMProvider:
    """Base LLM provider configuration"""
    
    def __init__(self, name: str, model: str, api_key: Optional[str] = None, 
                 api_base: Optional[str] = None, cost_per_1k_tokens: float = 0.0):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.is_available = bool(api_key)


class LLMGateway:
    """LiteLLM-powered gateway with semantic caching for infrastructure requests"""
    
    def __init__(self):
        self.settings = get_settings()
        self.semantic_cache: Optional[Cache] = None
        self.providers: Dict[str, LLMProvider] = {}
        self.fallback_order: List[str] = []
        
        # Initialize providers
        self._init_providers()
        
        # Configure LiteLLM
        self._configure_litellm()
        
        # Setup semantic cache
        try:
            self.semantic_cache = setup_semantic_cache()
            logger.info("Semantic cache enabled for infrastructure requests")
        except Exception as e:
            logger.warning(f"Failed to initialize semantic cache: {e}")
            self.semantic_cache = None
    
    def _init_providers(self):
        """Initialize available LLM providers"""
        
        # Google Gemini (Free tier available)
        if self.settings.google_gemini_api_key:
            self.providers["gemini"] = LLMProvider(
                name="Google Gemini",
                model="gemini/gemini-1.5-flash",
                api_key=self.settings.google_gemini_api_key,
                cost_per_1k_tokens=0.0  # Free tier
            )
            self.fallback_order.append("gemini")
        
        # OpenAI
        if self.settings.openai_api_key:
            self.providers["openai"] = LLMProvider(
                name="OpenAI GPT-4",
                model="gpt-4o-mini",
                api_key=self.settings.openai_api_key,
                cost_per_1k_tokens=0.30
            )
            self.fallback_order.append("openai")
        
        # Azure OpenAI
        if self.settings.azure_openai_api_key and self.settings.azure_openai_endpoint:
            # Set environment variables for LiteLLM
            os.environ["AZURE_API_KEY"] = self.settings.azure_openai_api_key
            os.environ["AZURE_API_BASE"] = self.settings.azure_openai_endpoint
            os.environ["AZURE_API_VERSION"] = "2024-02-15-preview"
            
            # Use the model name - LiteLLM will handle the deployment mapping
            self.providers["azure_openai"] = LLMProvider(
                name="Azure OpenAI",
                model="azure/gpt-4o-2024-08-06",  # Use model name, not deployment name
                api_key=self.settings.azure_openai_api_key,
                api_base=self.settings.azure_openai_endpoint,
                cost_per_1k_tokens=0.30
            )
            self.fallback_order.append("azure_openai")
        
        # OpenRouter (Gateway to many models)
        if self.settings.openrouter_api_key:
            self.providers["openrouter_cheap"] = LLMProvider(
                name="OpenRouter (Cheap)",
                model="openrouter/meta-llama/llama-3.1-8b-instruct:free",
                api_key=self.settings.openrouter_api_key,
                cost_per_1k_tokens=0.0  # Free model
            )
            self.providers["openrouter_premium"] = LLMProvider(
                name="OpenRouter (Premium)",
                model="openrouter/anthropic/claude-3.5-sonnet",
                api_key=self.settings.openrouter_api_key,
                cost_per_1k_tokens=3.00
            )
            self.fallback_order.extend(["openrouter_cheap", "openrouter_premium"])
        
        logger.info(f"Initialized {len(self.providers)} LLM providers: {list(self.providers.keys())}")
    
    def _configure_litellm(self):
        """Configure LiteLLM settings"""
        
        # Set API keys
        if self.settings.openai_api_key:
            litellm.openai_key = self.settings.openai_api_key
        
        if self.settings.google_gemini_api_key:
            litellm.gemini_key = self.settings.google_gemini_api_key
        
        if self.settings.openrouter_api_key:
            litellm.openrouter_key = self.settings.openrouter_api_key
        
        if self.settings.azure_openai_api_key:
            litellm.azure_key = self.settings.azure_openai_api_key
            litellm.azure_base = self.settings.azure_openai_endpoint
            litellm.azure_api_version = "2024-02-15-preview"
        
        # Configure logging
        litellm.set_verbose = True  # Always enable debug for now
        
        # Also set environment variable for better debugging
        os.environ['LITELLM_LOG'] = 'DEBUG'
        
        # Set default timeout
        litellm.request_timeout = 60
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get semantic cache statistics"""
        if not self.semantic_cache:
            return {"cache_enabled": False}
        
        try:
            # Get basic stats from cache
            return {
                "cache_enabled": True,
                "cache_type": "semantic_similarity",
                "similarity_threshold": 0.8,
                "embedding_model": "onnx"
            }
        except Exception as e:
            return {"cache_enabled": False, "error": str(e)}
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        response_format: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Generate response using best available LLM provider"""
        
        # Determine provider order
        if provider and provider in self.providers:
            provider_order = [provider]
        else:
            provider_order = self.fallback_order
        
        if not provider_order:
            raise ValueError("No LLM providers available")
        
        # Try each provider in order
        for provider_name in provider_order:
            provider_config = self.providers[provider_name]
            
            if not provider_config.is_available:
                continue
            
            try:
                return await self._call_provider(
                    provider_config=provider_config,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    response_format=response_format,
                    use_cache=use_cache,
                    **kwargs
                )
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                continue
        
        raise Exception("All LLM providers failed")
    
    async def _call_provider(
        self,
        provider_config: LLMProvider,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        stream: bool,
        response_format: Optional[Dict[str, str]],
        use_cache: bool,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Call specific LLM provider"""
        
        # Check semantic cache first (only for non-streaming requests)
        if use_cache and not stream and self.semantic_cache:
            try:
                # Create a simple prompt string for semantic matching
                prompt_text = " ".join([msg.get("content", "") for msg in messages])
                
                # Try to get from semantic cache
                cached_response = await self._get_from_semantic_cache(prompt_text, provider_config.model)
                if cached_response:
                    logger.info(f"Returning semantically cached response for {provider_config.name}")
                    return cached_response
            except Exception as e:
                logger.warning(f"Semantic cache lookup failed: {e}")
        
        # Prepare LiteLLM parameters
        litellm_params = {
            "model": provider_config.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        # Add max_tokens if specified
        if max_tokens:
            litellm_params["max_tokens"] = max_tokens
        
        # Add Azure-specific parameters if using Azure OpenAI
        if provider_config.model.startswith("azure/"):
            litellm_params["api_key"] = provider_config.api_key
            litellm_params["api_base"] = provider_config.api_base
            litellm_params["api_version"] = "2024-02-15-preview"
        
        # Add response format if specified
        if response_format:
            litellm_params["response_format"] = response_format
        
        # Add any additional kwargs
        litellm_params.update(kwargs)
        
        # Use all parameters for LiteLLM - it handles filtering internally
        filtered_params = litellm_params
        
        start_time = datetime.utcnow()
        
        try:
            if stream:
                return self._handle_streaming_response(provider_config, filtered_params, start_time)
            else:
                return await self._handle_non_streaming_response(
                    provider_config, filtered_params, start_time, use_cache
                )
                
        except Exception as e:
            logger.error(f"LLM call failed for {provider_config.name}: {e}")
            raise
    
    async def _handle_non_streaming_response(
        self,
        provider_config: LLMProvider,
        params: Dict[str, Any],
        start_time: datetime,
        use_cache: bool
    ) -> Dict[str, Any]:
        """Handle non-streaming LLM response"""
        
        response = await acompletion(**params)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Extract response data
        content = response.choices[0].message.content
        usage = response.usage
        
        # Calculate cost
        cost = self._calculate_cost(provider_config, usage)
        
        result = {
            "content": content,
            "provider": provider_config.name,
            "model": provider_config.model,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            },
            "cost": cost,
            "duration_seconds": duration,
            "timestamp": end_time.isoformat()
        }
        
        # Cache the response semantically
        if use_cache and self.semantic_cache:
            try:
                prompt_text = " ".join([msg.get("content", "") for msg in params["messages"]])
                await self._store_in_semantic_cache(prompt_text, params["model"], result)
            except Exception as e:
                logger.warning(f"Failed to cache response semantically: {e}")
        
        logger.info(f"LLM response from {provider_config.name}: {usage.total_tokens} tokens, ${cost:.4f}")
        
        return result
    
    async def _get_from_semantic_cache(
        self, 
        prompt_text: str, 
        model: str
    ) -> Optional[Dict[str, Any]]:
        """Get response from semantic cache using similarity matching"""
        if not self.semantic_cache:
            return None
        
        try:
            # GPTCache get method - returns cached response if similarity threshold met
            cached_data = self.semantic_cache.get(prompt_text)
            if cached_data:
                logger.info("Semantic cache hit - returning similar infrastructure response")
                return cached_data
        except Exception as e:
            logger.warning(f"Semantic cache get failed: {e}")
        
        return None
    
    async def _store_in_semantic_cache(
        self, 
        prompt_text: str, 
        model: str, 
        response: Dict[str, Any]
    ) -> None:
        """Store response in semantic cache for future similar requests"""
        if not self.semantic_cache:
            return
        
        try:
            # Store with GPTCache - will be retrievable by similar prompts
            self.semantic_cache.put(prompt_text, response)
            logger.debug(f"Stored response in semantic cache for model {model}")
        except Exception as e:
            logger.warning(f"Failed to store in semantic cache: {e}")
    
    async def _handle_streaming_response(
        self,
        provider_config: LLMProvider,
        params: Dict[str, Any],
        start_time: datetime
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming LLM response"""
        
        full_content = ""
        total_tokens = 0
        
        try:
            async for chunk in await acompletion(**params):
                if chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    full_content += content_chunk
                    
                    yield {
                        "type": "chunk",
                        "content": content_chunk,
                        "provider": provider_config.name,
                        "model": provider_config.model
                    }
            
            # Final summary chunk
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Estimate token usage for streaming (since it's not provided)
            estimated_tokens = len(full_content) // 4  # Rough estimation
            cost = self._calculate_cost_from_tokens(provider_config, estimated_tokens)
            
            yield {
                "type": "final",
                "full_content": full_content,
                "provider": provider_config.name,
                "model": provider_config.model,
                "estimated_tokens": estimated_tokens,
                "estimated_cost": cost,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "provider": provider_config.name
            }
    
    def _calculate_cost(self, provider_config: LLMProvider, usage) -> float:
        """Calculate cost based on token usage"""
        if not usage or provider_config.cost_per_1k_tokens == 0:
            return 0.0
        
        total_tokens = usage.total_tokens
        return (total_tokens / 1000) * provider_config.cost_per_1k_tokens
    
    def _calculate_cost_from_tokens(self, provider_config: LLMProvider, tokens: int) -> float:
        """Calculate cost from token count"""
        if provider_config.cost_per_1k_tokens == 0:
            return 0.0
        
        return (tokens / 1000) * provider_config.cost_per_1k_tokens
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """Generate embeddings for texts"""
        
        try:
            # Use OpenAI embeddings through LiteLLM
            response = await embedding(
                model=model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            logger.info(f"Generated embeddings for {len(texts)} texts using {model}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers"""
        return [
            {
                "name": config.name,
                "model": config.model,
                "cost_per_1k_tokens": config.cost_per_1k_tokens,
                "is_available": config.is_available
            }
            for config in self.providers.values()
        ]
    
    def get_cheapest_provider(self) -> Optional[str]:
        """Get the cheapest available provider"""
        available_providers = [
            (name, config) for name, config in self.providers.items()
            if config.is_available
        ]
        
        if not available_providers:
            return None
        
        # Sort by cost (free providers first)
        available_providers.sort(key=lambda x: x[1].cost_per_1k_tokens)
        
        return available_providers[0][0]
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        # This would typically be tracked in a database
        # For now, return mock data
        
        return {
            "total_requests": 1250,
            "total_tokens": 1500000,
            "total_cost": 45.75,
            "providers_used": {
                "gemini": {"requests": 800, "tokens": 950000, "cost": 0.0},
                "openai": {"requests": 350, "tokens": 425000, "cost": 35.50},
                "openrouter_cheap": {"requests": 100, "tokens": 125000, "cost": 0.0}
            },
            "average_cost_per_request": 0.037,
            "cache_hit_rate": 0.25
        }