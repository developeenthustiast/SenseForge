import sys
sys.path.append('..')

import torch
import json
import matplotlib.pyplot as plt
from model.jepa import LiquidityJEPA

def load_training_data(filepath='data/training_data.json'):
    """Load training dataset from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def train_jepa_model(num_epochs=50, batch_size=32):
    """
    Train the JEPA model on synthetic data.
    """
    print("Loading JEPA model...")
    jepa = LiquidityJEPA(state_dim=3, action_dim=1, latent_dim=16)
    
    # Try to load existing checkpoint
    if jepa.load_checkpoint():
        print("Resuming from checkpoint...")
    
    print("Loading training data...")
    dataset = load_training_data()
    print(f"Loaded {len(dataset)} episodes")
    
    # Populate replay buffer
    print("Populating replay buffer...")
    for episode in dataset:
        jepa.add_experience(
            state_dict=episode['initial_state'],
            action_value=episode['action'],
            next_state_dict=episode['next_state']
        )
    
    print(f"Replay buffer size: {len(jepa.replay_buffer)}")
    
    # Training loop
    print(f"\nTraining for {num_epochs} epochs...")
    for epoch in range(num_epochs):
        avg_loss = jepa.train_epoch(batch_size=batch_size, num_batches=10)
        
        if avg_loss is not None:
            print(f"Epoch {epoch + 1}/{num_epochs} - Loss: {avg_loss:.6f}")
        
        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            jepa.save_checkpoint()
    
    # Final save
    jepa.save_checkpoint()
    
    # Print training stats
    stats = jepa.get_training_stats()
    print("\n=== Training Complete ===")
    print(f"Epochs Trained: {stats['epochs_trained']}")
    print(f"Initial Loss: {stats['initial_loss']:.6f}")
    print(f"Final Loss: {stats['current_loss']:.6f}")
    print(f"Improvement: {stats['improvement']:.2f}%")
    
    return jepa

def visualize_training(jepa):
    """Create a visualization of the training loss curve."""
    if not jepa.training_history:
        print("No training history to visualize")
        return
    
    plt.figure(figsize=(10, 6))
    plt.plot(jepa.training_history, label='Training Loss', linewidth=2)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Mean Squared Error', fontsize=12)
    plt.title('JEPA Model Learning Curve', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Add improvement annotation
    stats = jepa.get_training_stats()
    plt.text(
        len(jepa.training_history) * 0.6, 
        max(jepa.training_history) * 0.8,
        f"Improvement: {stats['improvement']:.1f}%",
        fontsize=11,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    plt.tight_layout()
    plt.savefig('visualizations/jepa_learning_curve.png', dpi=150)
    print("\nLearning curve saved to visualizations/jepa_learning_curve.png")
    plt.show()

if __name__ == "__main__":
    # Train the model
    jepa = train_jepa_model(num_epochs=50, batch_size=32)
    
    # Visualize results
    visualize_training(jepa)
