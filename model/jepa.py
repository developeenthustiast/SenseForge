"""
SenseForge JEPA Model
Updated version with database integration and versioning.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import os
from datetime import datetime
from typing import Optional, Dict, List

from database.repository import CheckpointRepository, TrainingRepository
from metrics import metrics
from logging_setup import logger

class LiquidityJEPA(nn.Module):
    """Enhanced JEPA model with production features"""
    
    def __init__(self, state_dim: int = 3, action_dim: int = 1, latent_dim: int = 16):
        super().__init__()
        
        # Architecture (unchanged)
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim)
        )
        
        self.predictor = nn.Sequential(
            nn.Linear(latent_dim + action_dim, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim)
        )
        
        self.projector = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, state_dim)
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        self.loss_fn = nn.MSELoss()
        self.replay_buffer = deque(maxlen=10000)
        self.training_history: List[float] = []
        
        logger.info("LiquidityJEPA initialized")
    
    def forward(self, state_tensor):
        """Encode state to latent representation"""
        return self.encoder(state_tensor)
    
    def predict_next_state(self, current_state_tensor, action_tensor):
        """Predict next market state"""
        z_t = self.encoder(current_state_tensor)
        z_pred = self.predictor(torch.cat([z_t, action_tensor], dim=1))
        state_pred = self.projector(z_pred)
        return state_pred
    
    def train_epoch(self, batch_size=32, num_batches=10) -> Optional[float]:
        """Train for one epoch with metrics tracking"""
        
        if len(self.replay_buffer) < batch_size:
            logger.warning(f"Insufficient samples for training: {len(self.replay_buffer)}")
            return None
        
        epoch_losses = []
        
        for _ in range(num_batches):
            batch = random.sample(list(self.replay_buffer), batch_size)
            
            states, actions, next_states = zip(*batch)
            states_tensor = torch.stack(list(states))
            actions_tensor = torch.stack(list(actions))
            next_states_tensor = torch.stack(list(next_states))
            
            loss = self.train_step(states_tensor, actions_tensor, next_states_tensor)
            epoch_losses.append(loss)
        
        avg_loss = sum(epoch_losses) / len(epoch_losses)
        self.training_history.append(avg_loss)
        
        # Update metrics
        metrics.track_training(avg_loss)
        
        return avg_loss
    
    def train_step(self, current_state, action, next_state_target):
        """Single training step"""
        self.optimizer.zero_grad()
        
        pred_next_state = self.predict_next_state(current_state, action)
        loss = self.loss_fn(pred_next_state, next_state_target)
        
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def add_experience(self, state_dict: Dict, action_value: float, next_state_dict: Dict):
        """Add experience to replay buffer and database"""
        
        state_tensor = torch.tensor([[
            state_dict['liquidity_depth'],
            state_dict['volatility_index'],
            state_dict['governance_risk_score']
        ]], dtype=torch.float32)
        
        action_tensor = torch.tensor([[action_value]], dtype=torch.float32)
        
        next_state_tensor = torch.tensor([[
            next_state_dict['liquidity_depth'],
            next_state_dict['volatility_index'],
            next_state_dict['governance_risk_score']
        ]], dtype=torch.float32)
        
        self.replay_buffer.append((state_tensor, action_tensor, next_state_tensor))
        
        # Also save to database for persistent training data
        try:
            TrainingRepository.add_episode(
                initial_state=state_dict,
                action=action_value,
                next_state=next_state_dict
            )
        except Exception as e:
            logger.error(f"Failed to save training episode to database: {e}")
    
    def save_checkpoint_versioned(self, version: Optional[str] = None, notes: Optional[str] = None):
        """Save checkpoint with version tracking"""
        
        if version is None:
            version = datetime.now().strftime("v%Y%m%d_%H%M%S")
        
        filepath = f"checkpoints/jepa_model_{version}.pth"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        checkpoint = {
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history,
            'replay_buffer_size': len(self.replay_buffer),
            'version': version,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        torch.save(checkpoint, filepath)
        
        # Save metadata to database
        try:
            CheckpointRepository.save_checkpoint(
                version=version,
                epochs_trained=len(self.training_history),
                final_loss=self.training_history[-1] if self.training_history else 0.0,
                training_samples=len(self.replay_buffer),
                file_path=filepath,
                notes=notes,
                metadata={'replay_buffer_size': len(self.replay_buffer)}
            )
        except Exception as e:
            logger.error(f"Failed to save checkpoint metadata: {e}")
        
        logger.info(f"Checkpoint saved: {version}")
        
        return filepath
    
    def load_checkpoint_versioned(self, version: Optional[str] = None) -> bool:
        """Load checkpoint by version"""
        
        if version is None:
            # Load latest
            checkpoint_record = CheckpointRepository.get_latest()
            if not checkpoint_record:
                logger.warning("No checkpoints found")
                return False
            
            filepath = checkpoint_record.file_path
            logger.info(f"Loading latest checkpoint: {checkpoint_record.version}")
        else:
            checkpoint_record = CheckpointRepository.get_by_version(version)
            if not checkpoint_record:
                logger.warning(f"Checkpoint version {version} not found")
                return False
            
            filepath = checkpoint_record.file_path
        
        if not os.path.exists(filepath):
            logger.error(f"Checkpoint file not found: {filepath}")
            return False
        
        checkpoint = torch.load(filepath)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.training_history = checkpoint['training_history']
        
        logger.info(f"Checkpoint loaded from {filepath}")
        
        # Update metrics
        if self.training_history:
            metrics.track_training(self.training_history[-1])
        
        return True
    
    # Keep existing methods for backward compatibility
    def save_checkpoint(self, filepath='checkpoints/jepa_model.pth'):
        """Legacy save method"""
        return self.save_checkpoint_versioned()
    
    def load_checkpoint(self, filepath='checkpoints/jepa_model.pth'):
        """Legacy load method"""
        return self.load_checkpoint_versioned()

