"""
Smart LLM Provider Abstraction Layer
Handles routing between DeepSeek and OpenAI with intelligent fallback and cost tracking
"""

import os
import json
import time
import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

import openai
import litellm
from litellm import completion, acompletion

from app.core.config import settings

logger = logging.getLogger(__name__)

class TaskType(str, Enum):
    """Types of LLM tasks for routing decisions"""
    VALIDATION = "validation"
    EXTRACTION = "extraction" 
    PARSING = "parsing"
    CLASSIFICATION = "classification"
    RELEVANCE_CHECK = "relevance_check"
    EMBEDDING = "embedding"
    CRITICAL = "critical"

class LLMProvider(str, Enum):
    """Available LLM providers"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"

@dataclass
class UsageStats:
    """Track usage statistics per provider"""
    provider: LLMProvider
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    estimated_cost: float = 0.0
    last_used: Optional[datetime] = None
    average_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)

@dataclass
class LLMResponse:
    """Standardized LLM response format"""
    content: str
    provider_used: LLMProvider
    tokens_input: int
    tokens_output: int
    cost_estimate: float
    response_time: float
    fallback_used: bool = False

class SmartLLMProvider:
    """
    Smart LLM provider that routes tasks optimally between DeepSeek and OpenAI
    with automatic fallback and comprehensive monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize clients
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # DeepSeek configuration for LiteLLM
        self.deepseek_available = bool(settings.DEEPSEEK_API_KEY)
        if self.deepseek_available:
            os.environ["DEEPSEEK_API_KEY"] = settings.DEEPSEEK_API_KEY
        
        # Usage statistics
        self.stats = {
            LLMProvider.DEEPSEEK: UsageStats(LLMProvider.DEEPSEEK),
            LLMProvider.OPENAI: UsageStats(LLMProvider.OPENAI)
        }
        
        # Cost estimates per 1M tokens (input/output)
        self.cost_per_million_tokens = {
            LLMProvider.DEEPSEEK: {"input": 0.14, "output": 0.28},
            LLMProvider.OPENAI: {"input": 10.0, "output": 30.0}  # GPT-4 pricing
        }
        
        # Task routing configuration
        self.task_routing = {
            TaskType.VALIDATION: LLMProvider.DEEPSEEK,
            TaskType.EXTRACTION: LLMProvider.DEEPSEEK,
            TaskType.PARSING: LLMProvider.DEEPSEEK,
            TaskType.CLASSIFICATION: LLMProvider.DEEPSEEK,
            TaskType.RELEVANCE_CHECK: LLMProvider.DEEPSEEK,
            TaskType.EMBEDDING: LLMProvider.OPENAI,  # OpenAI only for embeddings
            TaskType.CRITICAL: LLMProvider.OPENAI    # Critical tasks use OpenAI
        }
        
        self.logger.info(f"SmartLLMProvider initialized. DeepSeek available: {self.deepseek_available}")

    async def chat_completion(
        self,
        task_type: TaskType,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.1,
        **kwargs
    ) -> LLMResponse:
        """
        Execute chat completion with smart provider routing
        """
        start_time = time.time()
        primary_provider = self._get_primary_provider(task_type)
        
        try:
            # Try primary provider first
            response = await self._execute_completion(
                provider=primary_provider,
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Record successful usage
            self._record_usage(primary_provider, response, start_time, success=True)
            
            return LLMResponse(
                content=response["content"],
                provider_used=primary_provider,
                tokens_input=response["tokens_input"],
                tokens_output=response["tokens_output"],
                cost_estimate=response["cost_estimate"],
                response_time=time.time() - start_time,
                fallback_used=False
            )
            
        except Exception as e:
            self.logger.warning(f"{primary_provider} failed: {e}. Attempting fallback...")
            
            # Record failed usage
            self._record_usage(primary_provider, None, start_time, success=False)
            
            # Try fallback provider
            fallback_provider = self._get_fallback_provider(primary_provider)
            
            try:
                response = await self._execute_completion(
                    provider=fallback_provider,
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                # Record successful fallback usage
                self._record_usage(fallback_provider, response, start_time, success=True)
                
                return LLMResponse(
                    content=response["content"],
                    provider_used=fallback_provider,
                    tokens_input=response["tokens_input"],
                    tokens_output=response["tokens_output"],
                    cost_estimate=response["cost_estimate"],
                    response_time=time.time() - start_time,
                    fallback_used=True
                )
                
            except Exception as fallback_error:
                self.logger.error(f"Both providers failed. Primary: {e}, Fallback: {fallback_error}")
                self._record_usage(fallback_provider, None, start_time, success=False)
                raise Exception(f"All LLM providers failed. Primary ({primary_provider}): {e}, Fallback ({fallback_provider}): {fallback_error}")

    async def _execute_completion(
        self,
        provider: LLMProvider,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.1,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute completion with specific provider"""
        
        if provider == LLMProvider.DEEPSEEK:
            if not self.deepseek_available:
                raise Exception("DeepSeek API key not available")
            
            # Use LiteLLM for DeepSeek
            model = model or "deepseek-chat"
            
            response = await acompletion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            content = response.choices[0].message.content
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens
            
        elif provider == LLMProvider.OPENAI:
            # Use OpenAI directly
            model = model or "gpt-4o-mini"  # Cost-effective OpenAI model
            
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            content = response.choices[0].message.content
            tokens_input = response.usage.prompt_tokens
            tokens_output = response.usage.completion_tokens
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Calculate cost estimate
        cost_estimate = self._calculate_cost(provider, tokens_input, tokens_output)
        
        return {
            "content": content,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost_estimate": cost_estimate
        }

    def _get_primary_provider(self, task_type: TaskType) -> LLMProvider:
        """Get primary provider for task type"""
        return self.task_routing.get(task_type, LLMProvider.DEEPSEEK)

    def _get_fallback_provider(self, primary_provider: LLMProvider) -> LLMProvider:
        """Get fallback provider"""
        return LLMProvider.OPENAI if primary_provider == LLMProvider.DEEPSEEK else LLMProvider.DEEPSEEK

    def _calculate_cost(self, provider: LLMProvider, tokens_input: int, tokens_output: int) -> float:
        """Calculate estimated cost for the request"""
        rates = self.cost_per_million_tokens[provider]
        input_cost = (tokens_input / 1_000_000) * rates["input"]
        output_cost = (tokens_output / 1_000_000) * rates["output"]
        return input_cost + output_cost

    def _record_usage(
        self,
        provider: LLMProvider,
        response: Optional[Dict[str, Any]],
        start_time: float,
        success: bool
    ):
        """Record usage statistics"""
        stats = self.stats[provider]
        stats.total_requests += 1
        stats.last_used = datetime.now()
        
        response_time = time.time() - start_time
        stats.response_times.append(response_time)
        
        # Keep only last 100 response times for average calculation
        if len(stats.response_times) > 100:
            stats.response_times = stats.response_times[-100:]
        
        stats.average_response_time = sum(stats.response_times) / len(stats.response_times)
        
        if success and response:
            stats.successful_requests += 1
            stats.total_tokens_input += response["tokens_input"]
            stats.total_tokens_output += response["tokens_output"]
            stats.estimated_cost += response["cost_estimate"]
        else:
            stats.failed_requests += 1

    def get_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive usage statistics"""
        return {
            provider.value: {
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": (stats.successful_requests / max(stats.total_requests, 1)) * 100,
                "total_tokens_input": stats.total_tokens_input,
                "total_tokens_output": stats.total_tokens_output,
                "total_tokens": stats.total_tokens_input + stats.total_tokens_output,
                "estimated_cost": round(stats.estimated_cost, 4),
                "average_response_time": round(stats.average_response_time, 3),
                "last_used": stats.last_used.isoformat() if stats.last_used else None
            }
            for provider, stats in self.stats.items()
        }

    def get_cost_savings_report(self) -> Dict[str, Any]:
        """Generate cost savings report comparing DeepSeek vs OpenAI usage"""
        deepseek_stats = self.stats[LLMProvider.DEEPSEEK]
        openai_stats = self.stats[LLMProvider.OPENAI]
        
        # Calculate what it would have cost if everything was on OpenAI
        deepseek_tokens = deepseek_stats.total_tokens_input + deepseek_stats.total_tokens_output
        hypothetical_openai_cost = (
            (deepseek_stats.total_tokens_input / 1_000_000) * self.cost_per_million_tokens[LLMProvider.OPENAI]["input"] +
            (deepseek_stats.total_tokens_output / 1_000_000) * self.cost_per_million_tokens[LLMProvider.OPENAI]["output"]
        )
        
        actual_cost = deepseek_stats.estimated_cost + openai_stats.estimated_cost
        savings = hypothetical_openai_cost - actual_cost
        savings_percentage = (savings / max(hypothetical_openai_cost, 0.01)) * 100
        
        return {
            "total_actual_cost": round(actual_cost, 4),
            "hypothetical_openai_only_cost": round(hypothetical_openai_cost, 4),
            "total_savings": round(savings, 4),
            "savings_percentage": round(savings_percentage, 2),
            "deepseek_requests": deepseek_stats.total_requests,
            "openai_requests": openai_stats.total_requests,
            "deepseek_tokens": deepseek_tokens,
            "openai_tokens": openai_stats.total_tokens_input + openai_stats.total_tokens_output
        }

# Global instance
_smart_llm_provider = None

def get_smart_llm_provider() -> SmartLLMProvider:
    """Get global SmartLLMProvider instance"""
    global _smart_llm_provider
    if _smart_llm_provider is None:
        _smart_llm_provider = SmartLLMProvider()
    return _smart_llm_provider

# Convenience functions for common tasks
async def validate_content(content: str, context: str = "") -> Dict[str, Any]:
    """Convenience function for content validation using optimal provider"""
    provider = get_smart_llm_provider()
    
    prompt = f"""
    Validate this extracted intelligence item data:
    
    Data: {content}
    Context: {context}
    
    Assess:
    1. Data quality and completeness
    2. Legitimacy of the opportunity
    3. Relevance for African AI development
    4. Confidence in extraction accuracy
    
    Return JSON with confidence_score (0-1) and validation notes.
    """
    
    messages = [{"role": "user", "content": prompt}]
    
    response = await provider.chat_completion(
        task_type=TaskType.VALIDATION,
        messages=messages,
        max_tokens=500,
        temperature=0.1
    )
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"confidence_score": 0.5, "notes": "Validation completed but response format invalid"}

async def check_relevance(title: str, content: str) -> Dict[str, Any]:
    """Convenience function for relevance checking using optimal provider"""
    provider = get_smart_llm_provider()
    
    prompt = f"""
    Check the relevance of this content for African AI funding opportunities:
    
    Title: {title}
    Content: {content[:1000]}
    
    Assess relevance on a scale of 0.0 to 1.0 and provide reasoning.
    Return JSON with relevance_score (0-1) and reasoning.
    """
    
    messages = [{"role": "user", "content": prompt}]
    
    response = await provider.chat_completion(
        task_type=TaskType.RELEVANCE_CHECK,
        messages=messages,
        max_tokens=200,
        temperature=0.1
    )
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"relevance_score": 0.5, "reasoning": "Relevance check completed but response format invalid"}
