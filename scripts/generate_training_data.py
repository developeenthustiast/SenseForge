import random
import json
from typing import List, Dict

def generate_synthetic_episode():
    """
    Generates a synthetic market episode:
    Initial State -> Event/Action -> Next State
    """
    # Initial market state
    base_liquidity = random.uniform(5_000_000, 15_000_000)
    base_volatility = random.uniform(0.1, 0.8)
    base_risk = random.uniform(0.0, 0.5)
    
    initial_state = {
        "liquidity_depth": base_liquidity,
        "volatility_index": base_volatility,
        "governance_risk_score": base_risk
    }
    
    # Random action (governance proposal)
    action_type = random.choice(["PASS", "REJECT", "NO_CHANGE"])
    action_value = 1.0 if action_type == "PASS" else (-1.0 if action_type == "REJECT" else 0.0)
    
    # Simulate market response
    # Rule: Risky proposals that pass -> liquidity drops
    # Rule: Risk rejected -> liquidity stabilizes
    liquidity_change = 0
    volatility_change = 0
    risk_change = 0
    
    if action_type == "PASS":
        if base_risk > 0.3:  # Risky proposal
            liquidity_change = -base_liquidity * random.uniform(0.05, 0.15)  # 5-15% drop
            volatility_change = random.uniform(0.1, 0.3)  # Volatility spikes
        else:  # Safe proposal
            liquidity_change = base_liquidity * random.uniform(0.01, 0.05)  # 1-5% increase
            volatility_change = random.uniform(-0.1, 0.1)
    elif action_type == "REJECT":
        liquidity_change = base_liquidity * random.uniform(0.0, 0.02)  # Slight stabilization
        volatility_change = random.uniform(-0.2, 0.0)
        risk_change = -base_risk * 0.2  # Risk decreases
    
    next_state = {
        "liquidity_depth": base_liquidity + liquidity_change,
        "volatility_index": max(0.1, min(1.0, base_volatility + volatility_change)),
        "governance_risk_score": max(0.0, min(1.0, base_risk + risk_change))
    }
    
    return {
        "initial_state": initial_state,
        "action": action_value,
        "action_type": action_type,
        "next_state": next_state
    }

def generate_training_dataset(num_episodes=100):
    """Generate a dataset of synthetic episodes."""
    dataset = []
    for i in range(num_episodes):
        episode = generate_synthetic_episode()
        dataset.append(episode)
    
    return dataset

def save_dataset(dataset: List[Dict], filepath='data/training_data.json'):
    """Save dataset to JSON file."""
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(dataset, f, indent=2)
    print(f"Saved {len(dataset)} episodes to {filepath}")

if __name__ == "__main__":
    print("Generating synthetic training dataset...")
    dataset = generate_training_dataset(num_episodes=150)
    save_dataset(dataset)
    
    # Print sample episode
    print("\nSample Episode:")
    sample = dataset[0]
    print(f"Initial State: {sample['initial_state']}")
    print(f"Action: {sample['action_type']} ({sample['action']})")
    print(f"Next State: {sample['next_state']}")
