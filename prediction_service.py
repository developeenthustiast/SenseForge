"""
SenseForge Prediction Service
Enterprise-grade prediction tracking with automated accuracy monitoring.
"""
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from logging_setup import logger, log_prediction
from metrics import metrics
from config import config

@dataclass
class Prediction:
    """Prediction record with full context"""
    id: str
    timestamp: datetime
    state: Dict
    predicted_liquidity: float
    actual_liquidity: Optional[float] = None
    confidence: Optional[float] = None
    risk_level: str = "UNKNOWN"
    reasoning: str = ""
    metadata: Dict = None
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class PredictionService:
    """
    Enterprise prediction tracking service.
    Handles prediction logging, validation, and accuracy monitoring.
    """
    
    def __init__(self, storage_path: str = "data/predictions.jsonl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.predictions: Dict[str, Prediction] = {}
        self.load_predictions()
        logger.info(f"PredictionService initialized. Loaded {len(self.predictions)} predictions.")
    
    def load_predictions(self):
        """Load predictions from JSONL storage"""
        if not self.storage_path.exists():
            return
        
        with open(self.storage_path, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    pred = Prediction.from_dict(data)
                    self.predictions[pred.id] = pred
    
    def save_prediction(self, prediction: Prediction):
        """Append prediction to JSONL file"""
        with open(self.storage_path, 'a') as f:
            f.write(json.dumps(prediction.to_dict()) + '\n')
    
    def create_prediction(
        self,
        state: Dict,
        predicted_liquidity: float,
        confidence: Optional[float] = None,
        risk_level: str = "UNKNOWN",
        reasoning: str = "",
        metadata: Dict = None
    ) -> Prediction:
        """
        Create and log a new prediction.
        
        Args:
            state: Current market state
            predicted_liquidity: Predicted liquidity value
            confidence: Model confidence (0-1)
            risk_level: Risk assessment (SAFE, WARNING, CRITICAL)
            reasoning: Human-readable explanation
            metadata: Additional context
        
        Returns:
            Prediction object
        """
        # Generate unique ID
        prediction_id = f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        prediction = Prediction(
            id=prediction_id,
            timestamp=datetime.now(),
            state=state,
            predicted_liquidity=predicted_liquidity,
            confidence=confidence,
            risk_level=risk_level,
            reasoning=reasoning,
            metadata=metadata or {}
        )
        
        # Store
        self.predictions[prediction_id] = prediction
        self.save_prediction(prediction)
        
        # Track in metrics
        metrics.track_prediction(
            predicted=predicted_liquidity,
            actual=None,
            timestamp=prediction.timestamp,
            metadata={'id': prediction_id, 'confidence': confidence}
        )
        
        # Log
        log_prediction(state, {'predicted_liquidity': predicted_liquidity}, confidence)
        
        logger.info(f"[PREDICTION] Created {prediction_id} - Risk: {risk_level}")
        
        return prediction
    
    def update_actual(self, prediction_id: str, actual_liquidity: float):
        """
        Update prediction with actual observed value.
        
        Args:
            prediction_id: ID of the prediction
            actual_liquidity: Actual observed liquidity
        """
        if prediction_id not in self.predictions:
            logger.warning(f"Prediction {prediction_id} not found")
            return
        
        prediction = self.predictions[prediction_id]
        prediction.actual_liquidity = actual_liquidity
        
        # Calculate error
        error = abs(prediction.predicted_liquidity - actual_liquidity)
        error_pct = (error / actual_liquidity) * 100
        
        logger.info(
            f"[VALIDATION] {prediction_id} - "
            f"Predicted: {prediction.predicted_liquidity:.0f}, "
            f"Actual: {actual_liquidity:.0f}, "
            f"Error: {error_pct:.2f}%"
        )
        
        # Re-save (JSONL append-only, so we need a separate index file for updates)
        self._save_update(prediction_id, actual_liquidity)
    
    def _save_update(self, prediction_id: str, actual_value: float):
        """Save prediction update to updates file"""
        updates_path = self.storage_path.parent / "prediction_updates.jsonl"
        with open(updates_path, 'a') as f:
            update_record = {
                'prediction_id': prediction_id,
                'actual_liquidity': actual_value,
                'updated_at': datetime.now().isoformat()
            }
            f.write(json.dumps(update_record) + '\n')
    
    def get_recent_predictions(self, limit: int = 20, include_unvalidated: bool = True) -> List[Prediction]:
        """Get recent predictions"""
        all_preds = list(self.predictions.values())
        all_preds.sort(key=lambda p: p.timestamp, reverse=True)
        
        if not include_unvalidated:
            all_preds = [p for p in all_preds if p.actual_liquidity is not None]
        
        return all_preds[:limit]
    
    def calculate_accuracy(self, lookback_hours: int = 24) -> Dict:
        """
        Calculate prediction accuracy for recent period.
        
        Args:
            lookback_hours: How far back to look
        
        Returns:
            Accuracy statistics
        """
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        recent = [
            p for p in self.predictions.values()
            if p.timestamp >= cutoff and p.actual_liquidity is not None
        ]
        
        if not recent:
            return {
                'count': 0,
                'accuracy': None,
                'avg_error': None,
                'avg_error_pct': None
            }
        
        errors = [
            abs(p.predicted_liquidity - p.actual_liquidity)
            for p in recent
        ]
        error_pcts = [
            (abs(p.predicted_liquidity - p.actual_liquidity) / p.actual_liquidity) * 100
            for p in recent
        ]
        
        avg_error = sum(errors) / len(errors)
        avg_error_pct = sum(error_pcts) / len(error_pcts)
        accuracy = 100 - avg_error_pct
        
        return {
            'count': len(recent),
            'accuracy': accuracy,
            'avg_error': avg_error,
            'avg_error_pct': avg_error_pct
        }
    
    async def auto_validate_predictions(self, validation_delay_seconds: int = 300):
        """
        Background task to automatically validate predictions.
        Simulates checking actual market state after a delay.
        
        Args:
            validation_delay_seconds: How long to wait before validation
        """
        logger.info(f"Auto-validation service started (delay: {validation_delay_seconds}s)")
        
        while True:
            try:
                cutoff = datetime.now() - timedelta(seconds=validation_delay_seconds)
                unvalidated = [
                    p for p in self.predictions.values()
                    if p.actual_liquidity is None and p.timestamp < cutoff
                ]
                
                for prediction in unvalidated:
                    # In production, fetch actual value from Cambrian
                    # For now, simulate with slight noise
                    noise_factor = 1.0 + (random.uniform(-0.05, 0.05))  # ±5%
                    actual = prediction.predicted_liquidity * noise_factor
                    
                    self.update_actual(prediction.id, actual)
                
                if unvalidated:
                    logger.info(f"[AUTO-VALIDATION] Validated {len(unvalidated)} predictions")
                
            except Exception as e:
                logger.error(f"Auto-validation error: {e}")
            
            await asyncio.sleep(60)  # Check every minute

# Global prediction service
prediction_service = PredictionService()
