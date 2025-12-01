"""
SenseForge Logging Infrastructure
Centralized logging with file rotation and structured output.
"""
import logging
import logging.handlers
import os
from pathlib import Path
from config import config

def setup_logging():
    """Configure enterprise-grade logging"""
    # Create logs directory
    log_dir = Path(config.logging.file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("senseforge")
    logger.setLevel(getattr(logging, config.logging.level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.logging.file_path,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(config.logging.format)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logging()

def log_api_call(api_name: str, endpoint: str, status: str, duration_ms: float = None):
    """Structured logging for API calls"""
    msg = f"[API] {api_name} - {endpoint} - {status}"
    if duration_ms:
        msg += f" ({duration_ms:.2f}ms)"
    logger.info(msg)

def log_prediction(state: dict, prediction: dict, confidence: float = None):
    """Structured logging for predictions"""
    logger.info(
        f"[PREDICTION] Liquidity: {state.get('liquidity_depth', 0):.0f} "
        f"→ {prediction.get('predicted_liquidity', 0):.0f} "
        f"(Confidence: {confidence or 0:.2%})"
    )

def log_error(component: str, error: Exception, context: str = ""):
    """Structured error logging"""
    logger.error(
        f"[ERROR] {component} - {type(error).__name__}: {str(error)}"
        f"{' - ' + context if context else ''}"
    )

def log_training(epoch: int, loss: float, improvement: float = None):
    """Structured logging for training"""
    msg = f"[TRAINING] Epoch {epoch} - Loss: {loss:.6f}"
    if improvement:
        msg += f" (Improvement: {improvement:.2f}%)"
    logger.info(msg)
