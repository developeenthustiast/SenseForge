"""
SenseForge Metrics Tracking
Enterprise-grade metrics for monitoring agent performance.
"""
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    # Running without numpy (Vercel)
    NUMPY_AVAILABLE = False
    np = None

class MetricsTracker:
    """Tracks and analyzes agent performance metrics"""
    
    def __init__(self, metrics_file: str = "data/metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.predictions: List[Dict] = []
        self.training_history: List[float] = []
        self.load_metrics()
    
    def load_metrics(self):
        """Load metrics from file"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                self.predictions = data.get('predictions', [])
                self.training_history = data.get('training_history', [])
    
    def save_metrics(self):
        """Save metrics to file"""
        data = {
            'predictions': self.predictions,
            'training_history': self.training_history,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def track_prediction(self, predicted: float, actual: Optional[float] = None, 
                        timestamp: datetime = None, metadata: dict = None):
        """
        Track a prediction for accuracy calculation.
        
        Args:
            predicted: Predicted value
            actual: Actual value (None if not yet known)
            timestamp: When prediction was made
            metadata: Additional context
        """
        prediction_record = {
            'timestamp': (timestamp or datetime.now()).isoformat(),
            'predicted': predicted,
            'actual': actual,
            'metadata': metadata or {}
        }
        self.predictions.append(prediction_record)
        self.save_metrics()
    
    def update_actual(self, index: int, actual: float):
        """Update the actual value for a prediction"""
        if 0 <= index < len(self.predictions):
            self.predictions[index]['actual'] = actual
            self.save_metrics()
    
    def track_training(self, loss: float):
        """Track a training epoch loss"""
        self.training_history.append(loss)
        self.save_metrics()
    
    def get_accuracy_stats(self) -> Dict:
        """Calculate prediction accuracy statistics"""
        completed_predictions = [p for p in self.predictions if p['actual'] is not None]
        
        if not completed_predictions or not NUMPY_AVAILABLE:
            return {
                'count': len(completed_predictions) if completed_predictions else 0,
                'accuracy': None,
                'mae': None,
                'rmse': None
            }
        
        predicted = np.array([p['predicted'] for p in completed_predictions])
        actual = np.array([p['actual'] for p in completed_predictions])
        
        # Mean Absolute Error
        mae = np.mean(np.abs(predicted - actual))
        
        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((predicted - actual) ** 2))
        
        # Accuracy (as percentage)
        accuracy = 100 - (mae / np.mean(actual) * 100)
        
        return {
            'count': len(completed_predictions),
            'accuracy': accuracy,
            'mae': mae,
            'rmse': rmse
        }
    
    def get_training_stats(self) -> Dict:
        """Calculate training statistics"""
        if not self.training_history:
            return {
                'epochs': 0,
                'initial_loss': None,
                'current_loss': None,
                'improvement': None
            }
        
        initial_loss = self.training_history[0]
        current_loss = self.training_history[-1]
        improvement = ((initial_loss - current_loss) / initial_loss) * 100
        
        return {
            'epochs': len(self.training_history),
            'initial_loss': initial_loss,
            'current_loss': current_loss,
            'improvement': improvement
        }
    
    def get_recent_predictions(self, limit: int = 20) -> List[Dict]:
        """Get recent predictions"""
        return self.predictions[-limit:]
    
    def clear_metrics(self):
        """Clear all metrics (use with caution)"""
        self.predictions = []
        self.training_history = []
        self.save_metrics()

# Global metrics tracker
metrics = MetricsTracker()
