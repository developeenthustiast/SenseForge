import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import json
import os

class ExperienceReplayBuffer:
    """Stores state transitions for training the JEPA model."""
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, next_state):
        """Store a transition."""
        self.buffer.append((state, action, next_state))
    
    def sample(self, batch_size):
        """Sample a random batch of transitions."""
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self):
        return len(self.buffer)

class LiquidityJEPA(nn.Module):
    def __init__(self, state_dim: int = 3, action_dim: int = 1, latent_dim: int = 16):
        super().__init__()
        # Encoder: Maps MarketState (liquidity, vol, risk) to Latent Space
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim)
        )
        
        # Predictor: Takes Latent State + Action (e.g., "Pass Proposal") -> Next Latent State
        self.predictor = nn.Sequential(
            nn.Linear(latent_dim + action_dim, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim)
        )
        
        # Projector: Maps Latent State back to Predicted MarketState (for loss calc)
        self.projector = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, state_dim)
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        self.loss_fn = nn.MSELoss()
        self.replay_buffer = ExperienceReplayBuffer(capacity=10000)
        self.training_history = []
        
        print("LiquidityJEPA initialized with training capabilities.")

    def forward(self, state_tensor):
        """Encodes the state."""
        return self.encoder(state_tensor)

    def predict_next_state(self, current_state_tensor, action_tensor):
        """
        Predicts the next market state given current state and action.
        Action: 1.0 (Proposal Pass), 0.0 (No Change), -1.0 (Proposal Reject)
        """
        z_t = self.encoder(current_state_tensor)
        z_pred = self.predictor(torch.cat([z_t, action_tensor], dim=1))
        state_pred = self.projector(z_pred)
        return state_pred

    def train_step(self, current_state, action, next_state_target):
        """One step of training."""
        self.optimizer.zero_grad()
        
        pred_next_state = self.predict_next_state(current_state, action)
        loss = self.loss_fn(pred_next_state, next_state_target)
        
        loss.backward()
        self.optimizer.step()
        return loss.item()
    
    def train_epoch(self, batch_size=32, num_batches=10):
        """
        Train for one epoch using the experience replay buffer.
        Returns average loss for this epoch.
        """
        if len(self.replay_buffer) < batch_size:
            print(f"Not enough samples in buffer ({len(self.replay_buffer)}). Skipping training.")
            return None
        
        epoch_losses = []
        for _ in range(num_batches):
            batch = self.replay_buffer.sample(batch_size)
            
            states, actions, next_states = zip(*batch)
            states_tensor = torch.stack([s for s in states])
            actions_tensor = torch.stack([a for a in actions])
            next_states_tensor = torch.stack([ns for ns in next_states])
            
            loss = self.train_step(states_tensor, actions_tensor, next_states_tensor)
            epoch_losses.append(loss)
        
        avg_loss = sum(epoch_losses) / len(epoch_losses)
        self.training_history.append(avg_loss)
        return avg_loss
    
    def add_experience(self, state_dict, action_value, next_state_dict):
        """Add a new experience to the replay buffer."""
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
        
        self.replay_buffer.push(state_tensor, action_tensor, next_state_tensor)
    
    def save_checkpoint(self, filepath='checkpoints/jepa_model.pth'):
        """Save model weights and training history."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        checkpoint = {
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history
        }
        torch.save(checkpoint, filepath)
        print(f"Checkpoint saved to {filepath}")
    
    def load_checkpoint(self, filepath='checkpoints/jepa_model.pth'):
        """Load model weights and training history."""
        if os.path.exists(filepath):
            checkpoint = torch.load(filepath)
            self.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.training_history = checkpoint['training_history']
            print(f"Checkpoint loaded from {filepath}")
            return True
        return False
    
    def get_training_stats(self):
        """Get training statistics."""
        if not self.training_history:
            return {
                'epochs_trained': 0,
                'current_loss': None,
                'initial_loss': None,
                'improvement': None
            }
        
        return {
            'epochs_trained': len(self.training_history),
            'current_loss': self.training_history[-1],
            'initial_loss': self.training_history[0],
            'improvement': ((self.training_history[0] - self.training_history[-1]) / self.training_history[0] * 100)
        }
