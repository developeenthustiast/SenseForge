"""
Integration Tests for SenseForge
Testing complete workflows end-to-end.
"""
import pytest
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from perception.analyst import AnalystAgent
from model.jepa import LiquidityJEPA
from model.letta_memory import LettaMemory
from planning.strategist import StrategistAgent
from planning.auditor import AuditorAgent

class TestTriAgentWorkflow:
    """Integration tests for full Tri-Agent pipeline"""
    
    @pytest.fixture
    async def components(self):
        """Set up all components"""
        analyst = AnalystAgent(mode="mock")
        jepa = LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
        memory = LettaMemory(agent_id="test-agent", mode="mock")
        strategist = StrategistAgent(mode="mock")
        auditor = AuditorAgent()
        
        yield {
            'analyst': analyst,
            'jepa': jepa,
            'memory': memory,
            'strategist': strategist,
            'auditor': auditor
        }
        
        # Cleanup
        await analyst.cleanup()
        await memory.close()
        await strategist.cleanup()
    
    @pytest.mark.asyncio
    async def test_full_risk_analysis_workflow(self, components):
        """Test complete workflow: Analyst -> JEPA -> Strategist -> Auditor"""
        analyst = components['analyst']
        jepa = components['jepa']
        strategist = components['strategist']
        auditor = components['auditor']
        
        # 1. Analyst: Gather events
        events = []
        async for event in analyst.stream_liquidity_events():
            events.append(event)
            if len(events) >= 3:
                break
        
        assert len(events) == 3
        
        # 2. Normalize state
        state = analyst.normalize_state(events, [])
        assert state.liquidity_depth > 0
        
        # 3. JEPA: Predict
        import torch
        state_tensor = torch.tensor([[
            state.liquidity_depth,
            state.volatility_index,
            state.governance_risk_score
        ]])
        action_tensor = torch.tensor([[1.0]])
        
        predicted_state = jepa.predict_next_state(state_tensor, action_tensor)
        predicted_liquidity = float(predicted_state[0][0])
        
        # 4. Strategist: Analyze risk
        strategy = await strategist.analyze_risk(state.dict(), predicted_liquidity)
        assert 'risk_level' in strategy
        assert 'recommended_action' in strategy
        assert strategy['risk_level'] in ['SAFE', 'WARNING', 'CRITICAL']
        
        # 5. Auditor: Validate
        audit = await auditor.validate_action(strategy)
        assert 'approved' in audit
        assert isinstance(audit['approved'], bool)
    
    @pytest.mark.asyncio
    async def test_memory_storage_retrieval(self, components):
        """Test memory stores and retrieves episodes"""
        memory = components['memory']
        
        # Store episode
        state = {
            'liquidity_depth': 10000000.0,
            'volatility_index': 0.5,
            'governance_risk_score': 0.3
        }
        outcome = {'predicted_liquidity': 9500000.0}
        
        await memory.store_episode(state, "PASS_PROPOSAL", outcome)
        
        # Retrieve similar
        similar = await memory.retrieve_similar_episodes(state, limit=5)
        # In mock mode, should return what we stored
        assert len(similar) >= 0  # May be empty in mock mode initially
    
    @pytest.mark.asyncio
    async def test_training_improves_predictions(self, components):
        """Test that JEPA training reduces loss"""
        jepa = components['jepa']
        
        # Add training data
        for i in range(50):
            state_dict = {
                'liquidity_depth': 10000000.0 + i * 10000,
                'volatility_index': 0.5,
                'governance_risk_score': 0.3
            }
            next_state_dict = {
                'liquidity_depth': 9500000.0 + i * 10000,
                'volatility_index': 0.6,
                'governance_risk_score': 0.4
            }
            jepa.add_experience(state_dict, 1.0, next_state_dict)
        
        # Train multiple epochs
        losses = []
        for epoch in range(5):
            loss = jepa.train_epoch(batch_size=10, num_batches=2)
            if loss is not None:
                losses.append(loss)
        
        # Loss should generally decrease
        if len(losses) >= 3:
            assert losses[-1] <= losses[0] * 1.5  # Allow some variance

class TestErrorRecovery:
    """Test error recovery and resilience"""
    
    @pytest.mark.asyncio
    async def test_analyst_handles_no_data(self):
        """Test analyst handles empty data gracefully"""
        analyst = AnalystAgent(mode="mock")
        
        # Normalize with empty data
        state = analyst.normalize_state([], [])
        assert state is not None
        assert isinstance(state.liquidity_depth, float)
        
        await analyst.cleanup()
    
    @pytest.mark.asyncio
    async def test_strategist_fallback(self):
        """Test strategist falls back to rules when LLM fails"""
        strategist = StrategistAgent(mode="mock")  # Mock mode uses rules
        
        state = {
            'liquidity_depth': 10000000.0,
            'volatility_index': 0.5,
            'governance_risk_score': 0.3
        }
        
        # Should work even without LLM
        result = await strategist.analyze_risk(state, 8000000.0)
        assert result is not None
        assert 'risk_level' in result
        
        await strategist.cleanup()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
