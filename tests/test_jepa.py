"""
Unit tests for JEPA Model
Enterprise-grade testing with fixtures and assertions.
"""
import pytest
import torch
import tempfile
import os
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from model.jepa import LiquidityJEPA, ExperienceReplayBuffer

class TestExperienceReplayBuffer:
    """Test suite for ExperienceReplayBuffer"""
    
    def test_initialization(self):
        """Test buffer initialization"""
        buffer = ExperienceReplayBuffer(capacity=100)
        assert len(buffer) == 0
        assert buffer.buffer.maxlen == 100
    
    def test_push_and_sample(self):
        """Test pushing and sampling experiences"""
        buffer = ExperienceReplayBuffer(capacity=10)
        
        # Add experiences
        state = torch.tensor([[1.0, 2.0, 3.0]])
        action = torch.tensor([[1.0]])
        next_state = torch.tensor([[1.1, 2.1, 3.1]])
        
        buffer.push(state, action, next_state)
        assert len(buffer) == 1
        
        # Add more
        for i in range(5):
            buffer.push(state, action, next_state)
        assert len(buffer) == 6
        
        # Sample
        batch = buffer.sample(3)
        assert len(batch) == 3
    
    def test_capacity_limit(self):
        """Test that buffer respects capacity limit"""
        buffer = ExperienceReplayBuffer(capacity=5)
        
        state = torch.tensor([[1.0, 2.0, 3.0]])
        action = torch.tensor([[1.0]])
        next_state = torch.tensor([[1.1, 2.1, 3.1]])
        
        # Add more than capacity
        for i in range(10):
            buffer.push(state, action, next_state)
        
        assert len(buffer) == 5  # Should not exceed capacity

class TestLiquidityJEPA:
    """Test suite for LiquidityJEPA model"""
    
    @pytest.fixture
    def model(self):
        """Create a test model instance"""
        return LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
    
    def test_initialization(self, model):
        """Test model initialization"""
        assert model is not None
        assert len(model.training_history) == 0
        assert len(model.replay_buffer) == 0
    
    def test_forward_pass(self, model):
        """Test forward pass through encoder"""
        state = torch.tensor([[10000000.0, 0.5, 0.3]])
        latent = model.forward(state)
        assert latent.shape == (1, 16)
    
    def test_prediction(self, model):
        """Test state prediction"""
        state = torch.tensor([[10000000.0, 0.5, 0.3]])
        action = torch.tensor([[1.0]])
        predicted = model.predict_next_state(state, action)
        assert predicted.shape == (1, 3)
    
    def test_add_experience(self, model):
        """Test adding experience to buffer"""
        state_dict = {
            'liquidity_depth': 10000000.0,
            'volatility_index': 0.5,
            'governance_risk_score': 0.3
        }
        next_state_dict = {
            'liquidity_depth': 9500000.0,
            'volatility_index': 0.6,
            'governance_risk_score': 0.4
        }
        
        model.add_experience(state_dict, 1.0, next_state_dict)
        assert len(model.replay_buffer) == 1
    
    def test_train_epoch(self, model):
        """Test training epoch"""
        # Add enough samples
        for i in range(50):
            state_dict = {
                'liquidity_depth': 10000000.0 + i * 1000,
                'volatility_index': 0.5,
                'governance_risk_score': 0.3
            }
            next_state_dict = {
                'liquidity_depth': 9500000.0 + i * 1000,
                'volatility_index': 0.6,
                'governance_risk_score': 0.4
            }
            model.add_experience(state_dict, 1.0, next_state_dict)
        
        # Train
        loss = model.train_epoch(batch_size=10, num_batches=2)
        assert loss is not None
        assert loss > 0
        assert len(model.training_history) == 1
    
    def test_checkpoint_save_load(self, model):
        """Test checkpoint save and load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = os.path.join(tmpdir, 'test_checkpoint.pth')
            
            # Add training history
            model.training_history = [0.5, 0.4, 0.3]
            
            # Save
            model.save_checkpoint(checkpoint_path)
            assert os.path.exists(checkpoint_path)
            
            # Load in new model
            new_model = LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
            loaded = new_model.load_checkpoint(checkpoint_path)
            assert loaded
            assert new_model.training_history == [0.5, 0.4, 0.3]
    
    def test_training_stats(self, model):
        """Test training statistics calculation"""
        # No training
        stats = model.get_training_stats()
        assert stats['epochs_trained'] == 0
        assert stats['current_loss'] is None
        
        # After training
        model.training_history = [1.0, 0.8, 0.6]
        stats = model.get_training_stats()
        assert stats['epochs_trained'] == 3
        assert stats['current_loss'] == 0.6
        assert stats['initial_loss'] == 1.0
        assert stats['improvement'] == pytest.approx(40.0, rel=1e-2)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
