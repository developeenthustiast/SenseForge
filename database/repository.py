"""
SenseForge Database Repository
Handles persistence for checkpoints and training data.
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import os

# Mock database for now - in production this would use SQLAlchemy
class CheckpointRecord:
    def __init__(self, version, file_path, metadata):
        self.version = version
        self.file_path = file_path
        self.metadata = metadata

class CheckpointRepository:
    """Repository for model checkpoints"""
    
    _checkpoints: Dict[str, CheckpointRecord] = {}
    
    @classmethod
    def save_checkpoint(cls, version: str, epochs_trained: int, final_loss: float, 
                       training_samples: int, file_path: str, notes: Optional[str] = None,
                       metadata: Optional[Dict] = None):
        """Save checkpoint metadata"""
        record = CheckpointRecord(
            version=version,
            file_path=file_path,
            metadata={
                'epochs_trained': epochs_trained,
                'final_loss': final_loss,
                'training_samples': training_samples,
                'notes': notes,
                'timestamp': datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
        cls._checkpoints[version] = record
        
        # Persist to disk (simple JSON for now)
        cls._persist()
        
    @classmethod
    def get_latest(cls) -> Optional[CheckpointRecord]:
        """Get latest checkpoint"""
        if not cls._checkpoints:
            cls._load()
            if not cls._checkpoints:
                return None
        
        # Sort by version (assuming timestamp-based versioning)
        latest_version = sorted(cls._checkpoints.keys())[-1]
        return cls._checkpoints[latest_version]
    
    @classmethod
    def get_by_version(cls, version: str) -> Optional[CheckpointRecord]:
        """Get checkpoint by version"""
        if not cls._checkpoints:
            cls._load()
        return cls._checkpoints.get(version)
    
    @classmethod
    def _persist(cls):
        """Save to JSON file"""
        data = {
            v: {'file_path': r.file_path, 'metadata': r.metadata}
            for v, r in cls._checkpoints.items()
        }
        os.makedirs('data', exist_ok=True)
        with open('data/checkpoints.json', 'w') as f:
            json.dump(data, f, indent=2)
            
    @classmethod
    def _load(cls):
        """Load from JSON file"""
        if os.path.exists('data/checkpoints.json'):
            try:
                with open('data/checkpoints.json', 'r') as f:
                    data = json.load(f)
                cls._checkpoints = {
                    v: CheckpointRecord(v, d['file_path'], d['metadata'])
                    for v, d in data.items()
                }
            except Exception as e:
                print(f"Error loading checkpoints: {e}")

class TrainingRepository:
    """Repository for training episodes"""
    
    @classmethod
    def add_episode(cls, initial_state: Dict, action: float, next_state: Dict):
        """Add training episode"""
        episode = {
            'initial_state': initial_state,
            'action': action,
            'next_state': next_state,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Append to JSONL file
        os.makedirs('data', exist_ok=True)
        with open('data/training_episodes.jsonl', 'a') as f:
            f.write(json.dumps(episode) + '\n')
