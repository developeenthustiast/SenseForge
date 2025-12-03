"""
SenseForge Proof of Reasoning Logger
Generates audit trails for Verisense compliance and transparency.
"""
import json
from typing import Dict, List, Optional
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass, asdict
from uuid import UUID

from logging_setup import logger

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """Handle datetime, date, and UUID serialization for JSON"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

@dataclass
class ReasoningStep:
    """Single step in the reasoning chain"""
    step_number: int
    component: str  # "Analyst", "Brain", "Strategist", "Auditor"
    input_data: Dict
    output_data: Dict
    reasoning: str
    confidence: Optional[float] = None
    duration_ms: Optional[float] = None

@dataclass
class ReasoningChain:
    """Complete reasoning chain for one decision"""
    chain_id: str
    timestamp: datetime
    query: str
    steps: List[ReasoningStep]
    final_decision: Dict
    total_duration_ms: float
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'chain_id': self.chain_id,
            'timestamp': self.timestamp.isoformat(),
            'query': self.query,
            'steps': [asdict(s) for s in self.steps],
            'final_decision': self.final_decision,
            'total_duration_ms': self.total_duration_ms,
            'verisense_compliant': True,
            'schema_version': '1.0'
        }

class ProofOfReasoningLogger:
    """
    Enterprise audit trail generator for AI decisions.
    Provides complete transparency for Verisense network compliance.
    """
    
    def __init__(self, output_dir: str = "data/reasoning_logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_chain: Optional[ReasoningChain] = None
        logger.info("ProofOfReasoningLogger initialized")
    
    def start_chain(self, query: str) -> str:
        """
        Start a new reasoning chain.
        
        Args:
            query: The query/request being processed
        
        Returns:
            Chain ID
        """
        chain_id = f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.current_chain = ReasoningChain(
            chain_id=chain_id,
            timestamp=datetime.now(),
            query=query,
            steps=[],
            final_decision={},
            total_duration_ms=0.0
        )
        
        logger.info(f"[REASONING] Started chain {chain_id}")
        return chain_id
    
    def log_step(
        self,
        component: str,
        input_data: Dict,
        output_data: Dict,
        reasoning: str,
        confidence: Optional[float] = None,
        duration_ms: Optional[float] = None
    ):
        """
        Log a step in the reasoning chain.
        
        Args:
            component: Which component is reasoning (Analyst, Brain, Strategist, Auditor)
            input_data: Input to this step
            output_data: Output from this step
            reasoning: Human-readable explanation of what happened
            confidence: Confidence score (0-1)
            duration_ms: How long this step took
        """
        if not self.current_chain:
            logger.warning("No active reasoning chain. Call start_chain() first.")
            return
        
        step = ReasoningStep(
            step_number=len(self.current_chain.steps) + 1,
            component=component,
            input_data=input_data,
            output_data=output_data,
            reasoning=reasoning,
            confidence=confidence,
            duration_ms=duration_ms
        )
        
        self.current_chain.steps.append(step)
        logger.debug(f"[REASONING] Step {step.step_number}: {component}")
    
    def finalize_chain(self, final_decision: Dict, total_duration_ms: float):
        """
        Finalize the reasoning chain and save to disk.
        
        Args:
            final_decision: The final output/decision
            total_duration_ms: Total time for the entire chain
        """
        if not self.current_chain:
            logger.warning("No active reasoning chain to finalize")
            return
        
        self.current_chain.final_decision = final_decision
        self.current_chain.total_duration_ms = total_duration_ms
        
        # Save to file
        filename = f"{self.current_chain.chain_id}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.current_chain.to_dict(), f, indent=2, cls=DateTimeEncoder)
        
        logger.info(
            f"[REASONING] Finalized chain {self.current_chain.chain_id} "
            f"({len(self.current_chain.steps)} steps, {total_duration_ms:.2f}ms)"
        )
        
        # Clear current chain
        self.current_chain = None
    
    def generate_summary_report(self, lookback_hours: int = 24) -> Dict:
        """
        Generate a summary report of recent reasoning chains.
        
        Args:
            lookback_hours: How far back to analyze
        
        Returns:
            Summary statistics
        """
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        
        # Load all recent chains
        chains = []
        for filepath in self.output_dir.glob("chain_*.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data['timestamp'])
                if timestamp >= cutoff:
                    chains.append(data)
        
        if not chains:
            return {
                'count': 0,
                'avg_duration_ms': None,
                'avg_steps': None,
                'components_used': []
            }
        
        avg_duration = sum(c['total_duration_ms'] for c in chains) / len(chains)
        avg_steps = sum(len(c['steps']) for c in chains) / len(chains)
        
        # Component usage
        component_counts = {}
        for chain in chains:
            for step in chain['steps']:
                comp = step['component']
                component_counts[comp] = component_counts.get(comp, 0) + 1
        
        return {
            'count': len(chains),
            'avg_duration_ms': avg_duration,
            'avg_steps': avg_steps,
            'components_used': component_counts
        }

# Global logger instance
reasoning_logger = ProofOfReasoningLogger()
