"""
SenseForge Resilience Utilities
Enterprise-grade retry logic and circuit breakers for external dependencies.
"""
import asyncio
import time
from typing import Callable, Optional, Any, Dict
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta

from logging_setup import logger

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Enterprise circuit breaker pattern implementation.
    Prevents cascading failures by blocking requests to failing services.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Exception = Exception
    ):
        """
        Args:
            name: Circuit breaker name for logging
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            expected_exception: Exception type to catch
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"[Circuit Breaker] {self.name} entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"[Circuit Breaker] {self.name} recovered, returning to CLOSED")
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failure"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"[Circuit Breaker] {self.name} OPENED after "
                f"{self.failure_count} failures"
            )
    
    def get_state(self) -> Dict:
        """Get current circuit state"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None
        }

async def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to delay
        exceptions: Tuple of exceptions to catch
    
    Returns:
        Function result if successful
    
    Raises:
        Last exception if all retries fail
    """
    import random
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            
            if attempt == max_attempts - 1:
                logger.error(f"[Retry] All {max_attempts} attempts failed: {e}")
                raise e
            
            # Calculate delay with exponential backoff
            delay = min(initial_delay * (exponential_base ** attempt), max_delay)
            
            # Add jitter
            if jitter:
                delay = delay * (0.5 + random.random())
            
            logger.warning(
                f"[Retry] Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            
            await asyncio.sleep(delay)
    
    raise last_exception

def with_retry(max_attempts: int = 3, initial_delay: float = 1.0):
    """
    Decorator for adding retry logic to async functions.
    
    Usage:
        @with_retry(max_attempts=3, initial_delay=2.0)
        async def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                initial_delay=initial_delay
            )
        return wrapper
    return decorator

class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, rate: int, per: float):
        """
        Args:
            rate: Number of requests
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
    
    async def acquire(self):
        """Wait until a token is available"""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        
        self.allowance += time_passed * (self.rate / self.per)
        
        if self.allowance > self.rate:
            self.allowance = self.rate
        
        if self.allowance < 1.0:
            sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
            await asyncio.sleep(sleep_time)
            self.allowance = 0.0
        else:
            self.allowance -= 1.0
