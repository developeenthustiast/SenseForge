"""
SenseForge Strategist Agent
Enhanced with enterprise-grade Ambient LLM integration.
"""
from typing import Dict
import asyncio

from ambient_client import ambient_client
from logging_setup import logger

class StrategistAgent:
    """
    The Strategist interprets JEPA predictions and formulates risk assessments.
    Now powered by Ambient LLM for natural language reasoning.
    """
    
    def __init__(self, mode: str = "live"):
        """
        Args:
            mode: "mock" (rule-based) or "live" (LLM-powered)
        """
        self.mode = mode
        logger.info(f"StrategistAgent initialized (mode: {mode})")

    async def analyze_risk(self, current_state: dict, predicted_liquidity: float) -> dict:
        """
        Analyze risk based on JEPA prediction.
        
        Args:
            current_state: Current market state
            predicted_liquidity: JEPA model's liquidity prediction
        
        Returns:
            Risk assessment with recommendation
        """
        if self.mode == "live":
            # Use Ambient LLM for analysis
            try:
                analysis = await ambient_client.analyze_risk(
                    current_state,
                    predicted_liquidity
                )
                return analysis
            except Exception as e:
                logger.error(f"[Strategist] LLM analysis failed, falling back to rules: {e}")
                return self._rule_based_analysis(current_state, predicted_liquidity)
        else:
            # Mock mode: use rule-based logic
            return self._rule_based_analysis(current_state, predicted_liquidity)
    
    def _rule_based_analysis(self, current_state: dict, predicted_liquidity: float) -> dict:
        """Rule-based fallback analysis"""
        current_liq = current_state.get('liquidity_depth', 0)
        
        # Calculate drop percentage
        if current_liq > 0:
            drop_pct = ((current_liq - predicted_liquidity) / current_liq) * 100
        else:
            drop_pct = 0
        
        # Risk thresholds
        if drop_pct > 10:
            risk_level = "CRITICAL"
            action = "ALERT_DAO_TREASURY"
            reasoning = f"Predicted liquidity drop of {drop_pct:.1f}% exceeds safety threshold."
        elif drop_pct > 5:
            risk_level = "WARNING"
            action = "MONITOR"
            reasoning = f"Moderate risk detected. {drop_pct:.1f}% liquidity reduction predicted."
        else:
            risk_level = "SAFE"
            action = "MONITOR"
            reasoning = "Market conditions appear stable."
        
        return {
            "risk_level": risk_level,
            "recommended_action": action,
            "reasoning": reasoning,
            "confidence": 0.8,
            "method": "rule_based"
        }
    
    async def explain_decision(self, event: str, before: float, after: float, cause: str) -> str:
        """Generate human-readable explanation of a decision"""
        if self.mode == "live":
            try:
                explanation = await ambient_client.explain_crisis(event, before, after, cause)
                return explanation
            except Exception as e:
                logger.error(f"[Strategist] Explanation generation failed: {e}")
                return f"{event}: {cause}"
        else:
            return f"{event}: {cause}. Liquidity changed from ${before:,.0f} to ${after:,.0f}."
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.mode == "live":
            await ambient_client.close()
