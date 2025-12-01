"""
Unit tests for Resilience Utilities
Testing circuit breakers, retry logic, and rate limiting.
"""
import pytest
import asyncio
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from resilience import CircuitBreaker, retry_with_backoff, RateLimiter, CircuitState

class TestCircuitBreaker:
    """Test suite for CircuitBreaker"""
    
    @pytest.mark.asyncio
    async def test_normal_operation(self):
        """Test circuit breaker in closed state"""
        cb = CircuitBreaker("test", failure_threshold=3)
        
        async def successful_call():
            return "success"
        
        result = await cb.call(successful_call)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_opens_on_failures(self):
        """Test circuit opens after threshold failures"""
        cb = CircuitBreaker("test", failure_threshold=3)
        
        async def failing_call():
            raise Exception("Test failure")
        
        # First 3 failures should not open circuit yet
        for i in range(3):
            with pytest.raises(Exception):
                await cb.call(failing_call)
        
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3
    
    @pytest.mark.asyncio
    async def test_blocks_when_open(self):
        """Test circuit blocks calls when open"""
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=60)
        
        async def failing_call():
            raise Exception("Test failure")
        
        # Trigger opening
        for i in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_call)
        
        assert cb.state == CircuitState.OPEN
        
        # Should block now
        with pytest.raises(Exception, match="Circuit breaker .* is OPEN"):
            await cb.call(failing_call)
    
    @pytest.mark.asyncio
    async def test_half_open_recovery(self):
        """Test circuit transitions to half-open"""
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=1)
        
        async def failing_call():
            raise Exception("Test failure")
        
        async def successful_call():
            return "success"
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_call)
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Next call should enter HALF_OPEN and succeed
        result = await cb.call(successful_call)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

class TestRetryWithBackoff:
    """Test suite for retry_with_backoff"""
    
    @pytest.mark.asyncio
    async def test_succeeds_on_first_try(self):
        """Test successful call on first attempt"""
        async def successful_call():
            return "success"
        
        result = await retry_with_backoff(successful_call, max_attempts=3)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retries_on_failure(self):
        """Test retries transient failures"""
        call_count = 0
        
        async def flaky_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await retry_with_backoff(flaky_call, max_attempts=5, initial_delay=0.1)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_fails_after_max_attempts(self):
        """Test fails after exhausting retries"""
        async def failing_call():
            raise ValueError("Permanent failure")
        
        with pytest.raises(ValueError, match="Permanent failure"):
            await retry_with_backoff(failing_call, max_attempts=3, initial_delay=0.1)

class TestRateLimiter:
    """Test suite for RateLimiter"""
    
    @pytest.mark.asyncio
    async def test_allows_within_rate(self):
        """Test allows calls within rate limit"""
        limiter = RateLimiter(rate=10, per=1.0)
        
        start = datetime.now()
        for i in range(5):
            await limiter.acquire()
        duration = (datetime.now() - start).total_seconds()
        
        # Should be fast since we're under the limit
        assert duration < 0.5
    
    @pytest.mark.asyncio
    async def test_throttles_above_rate(self):
        """Test throttles calls above rate limit"""
        limiter = RateLimiter(rate=2, per=1.0)
        
        start = datetime.now()
        for i in range(4):  # More than rate
            await limiter.acquire()
        duration = (datetime.now() - start).total_seconds()
        
        # Should take at least 1 second (to allow 2 more requests)
        assert duration >= 0.9

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
