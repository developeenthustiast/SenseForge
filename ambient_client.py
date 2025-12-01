"""
SenseForge Ambient LLM Client
Enterprise-grade LLM integration with resilience patterns.
"""
import aiohttp
import asyncio
from typing import Dict, Optional, List
import os
import json
from datetime import datetime

from config import config
from logging_setup import logger, log_api_call
from resilience import CircuitBreaker, retry_with_backoff, RateLimiter

class PromptTemplate:
    """Structured prompt templates for consistent LLM interactions"""
    
    RISK_ANALYSIS = """You are an institutional risk analyst for DeFi protocols.

Current Market State:
- Liquidity Depth: ${liquidity:,.0f}
- Volatility Index: {volatility:.2f}
- Governance Risk Score: {risk_score:.2f}

JEPA Model Prediction:
- Predicted Liquidity (if proposal passes): ${predicted_liquidity:,.0f}
- Change: {change:.1f}%

Your task: Analyze the risk and provide a clear recommendation.

Respond in JSON format:
{{
  "risk_level": "SAFE" | "WARNING" | "CRITICAL",
  "recommended_action": "MONITOR" | "ALERT_DAO_TREASURY" | "BLOCK_PROPOSAL",
  "reasoning": "2-3 sentence explanation",
  "confidence": 0.0-1.0
}}"""

    CRISIS_EXPLANATION = """Explain the following liquidity crisis to DAO members:

Event: {event_description}
Impact: Liquidity dropped from ${before:,.0f} to ${after:,.0f}
Cause: {cause}

Generate a clear, professional explanation in 2-3 sentences."""

class AmbientLLMClient:
    """
    Production-grade Ambient LLM client with enterprise resilience.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.ambient.ai",
        model: str = "ambient-1",
        max_retries: int = 3,
        timeout: int = 30
    ):
        self.api_key = api_key or config.api.ambient_api_key
        self.base_url = base_url
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Enterprise resilience
        self.circuit_breaker = CircuitBreaker(
            name="AmbientLLM",
            failure_threshold=5,
            recovery_timeout=60
        )
        self.rate_limiter = RateLimiter(rate=10, per=60)  # 10 req/min
        
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"AmbientLLMClient initialized (model: {self.model})")
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            headers = {
                "Content-Type": "application/json"
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, prompt: str, temperature: float = 0.7) -> Dict:
        """Make LLM API request with retry and circuit breaker"""
        await self._ensure_session()
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        # Request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": 500
        }
        
        start_time = datetime.now()
        
        async def _call_api():
            url = f"{self.base_url}/v1/completions"
            async with self.session.post(url, json=payload, timeout=self.timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
        
        try:
            # Apply circuit breaker and retry logic
            result = await self.circuit_breaker.call(
                lambda: retry_with_backoff(
                    _call_api,
                    max_attempts=self.max_retries,
                    initial_delay=1.0
                )
            )
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            log_api_call("Ambient", "/v1/completions", "success", duration_ms)
            
            return result
        
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            log_api_call("Ambient", "/v1/completions", f"error: {e}", duration_ms)
            raise e
    
    async def analyze_risk(
        self,
        current_state: Dict,
        predicted_liquidity: float
    ) -> Dict:
        """
        Analyze risk using LLM reasoning.
        
        Args:
            current_state: Current market state
            predicted_liquidity: JEPA model prediction
        
        Returns:
            Risk analysis with recommendation
        """
        # Calculate change percentage
        current_liq = current_state.get('liquidity_depth', 0)
        change_pct = ((predicted_liquidity - current_liq) / current_liq) * 100 if current_liq > 0 else 0
        
        # Format prompt
        prompt = PromptTemplate.RISK_ANALYSIS.format(
            liquidity=current_liq,
            volatility=current_state.get('volatility_index', 0),
            risk_score=current_state.get('governance_risk_score', 0),
            predicted_liquidity=predicted_liquidity,
            change=change_pct
        )
        
        try:
            response = await self._make_request(prompt, temperature=0.3)
            
            # Parse JSON response
            text = response.get('choices', [{}])[0].get('text', '{}')
            analysis = json.loads(text)
            
            logger.info(
                f"[Ambient LLM] Risk analysis: {analysis.get('risk_level')} - "
                f"{analysis.get('recommended_action')}"
            )
            
            return analysis
        
        except json.JSONDecodeError as e:
            logger.error(f"[Ambient LLM] Failed to parse response as JSON: {e}")
            # Fallback to rule-based analysis
            return self._fallback_risk_analysis(current_state, predicted_liquidity)
        
        except Exception as e:
            logger.error(f"[Ambient LLM] Analysis failed: {e}")
            return self._fallback_risk_analysis(current_state, predicted_liquidity)
    
    def _fallback_risk_analysis(self, current_state: Dict, predicted_liquidity: float) -> Dict:
        """Fallback rule-based analysis when LLM fails"""
        current_liq = current_state.get('liquidity_depth', 0)
        change_pct = ((predicted_liquidity - current_liq) / current_liq) * 100 if current_liq > 0 else 0
        
        if change_pct < -10:
            risk_level = "CRITICAL"
            action = "ALERT_DAO_TREASURY"
            reasoning = f"Predicted liquidity drop of {abs(change_pct):.1f}% exceeds critical threshold."
        elif change_pct < -5:
            risk_level = "WARNING"
            action = "MONITOR"
            reasoning = f"Moderate liquidity drop of {abs(change_pct):.1f}% detected."
        else:
            risk_level = "SAFE"
            action = "MONITOR"
            reasoning = "Market conditions are stable."
        
        logger.info(f"[Fallback Analysis] {risk_level} - {action}")
        
        return {
            "risk_level": risk_level,
            "recommended_action": action,
            "reasoning": reasoning,
            "confidence": 0.7,
            "fallback": True
        }
    
    async def explain_crisis(self, event_description: str, before: float, after: float, cause: str) -> str:
        """Generate human-readable crisis explanation"""
        prompt = PromptTemplate.CRISIS_EXPLANATION.format(
            event_description=event_description,
            before=before,
            after=after,
            cause=cause
        )
        
        try:
            response = await self._make_request(prompt, temperature=0.5)
            explanation = response.get('choices', [{}])[0].get('text', '').strip()
            return explanation
        except Exception as e:
            logger.error(f"[Ambient LLM] Crisis explanation failed: {e}")
            return f"Liquidity crisis: {cause}. Impact: ${before:,.0f} → ${after:,.0f}"
    
    def get_health_status(self) -> Dict:
        """Get client health status"""
        return {
            'circuit_breaker': self.circuit_breaker.get_state(),
            'session_active': self.session is not None and not self.session.closed,
            'api_key_configured': self.api_key is not None
        }

# Global client instance
ambient_client = AmbientLLMClient()
