
"""
SenseForge Rate Limiting
Enterprise-grade rate limiting with multiple strategies.
"""
import time
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
import redis.asyncio as redis
import os

class RateLimiter:
    """
    Token bucket rate limiter with multiple storage backends.
    """
    
    def __init__(
        self,
        rate: int = 100,
        per: float = 60,
        storage: str = 'memory',
        redis_url: Optional[str] = None
    ):
        """
        Args:
            rate: Number of allowed requests
            per: Time period in seconds
            storage: 'memory' or 'redis'
            redis_url: Redis connection URL for distributed rate limiting
        """
        self.rate = rate
        self.per = per
        self.storage = storage
        
        if storage == 'redis':
            redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
        else:
            # In-memory storage
            self.allowances: Dict[str, float] = {}
            self.last_check: Dict[str, float] = {}
    
    async def is_allowed(self, key: str) -> tuple[bool, Dict]:
        """
        Check if request is allowed under rate limit.
        
        Returns:
            (allowed: bool, info: Dict)
        """
        if self.storage == 'redis':
            return await self._check_redis(key)
        else:
            return await self._check_memory(key)
    
    async def _check_memory(self, key: str) -> tuple[bool, Dict]:
        """Memory-based rate limiting"""
        current = time.time()
        
        if key not in self.last_check:
            self.last_check[key] = current
            self.allowances[key] = self.rate
        
        time_passed = current - self.last_check[key]
        self.last_check[key] = current
        
        # Refill tokens
        self.allowances[key] += time_passed * (self.rate / self.per)
        if self.allowances[key] > self.rate:
            self.allowances[key] = self.rate
        
        if self.allowances[key] >= 1.0:
            self.allowances[key] -= 1.0
            return True, {
                'remaining': int(self.allowances[key]),
                'reset': int(current + self.per)
            }
        else:
            retry_after = int((1.0 - self.allowances[key]) * (self.per / self.rate))
            return False, {
                'remaining': 0,
                'reset': int(current + self.per),
                'retry_after': retry_after
            }
    
    async def _check_redis(self, key: str) -> tuple[bool, Dict]:
        """Redis-based distributed rate limiting"""
        redis_key = f"ratelimit:{key}"
        
        # Use Redis sorted set for sliding window
        current = time.time()
        window_start = current - self.per
        
        # Remove old entries
        await self.redis_client.zremrangebyscore(redis_key, 0, window_start)
        
        # Count requests in window
        count = await self.redis_client.zcard(redis_key)
        
        if count < self.rate:
            # Add new request
            await self.redis_client.zadd(redis_key, {str(current): current})
            await self.redis_client.expire(redis_key, int(self.per) + 1)
            
            return True, {
                'remaining': self.rate - count - 1,
                'reset': int(current + self.per)
            }
        else:
            # Get oldest request time to calculate retry_after
            oldest = await self.redis_client.zrange(redis_key, 0, 0, withscores=True)
            retry_after = int(oldest[0][1] + self.per - current) if oldest else int(self.per)
            
            return False, {
                'remaining': 0,
                'reset': int(current + self.per),
                'retry_after': retry_after
            }

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Starlette middleware for rate limiting"""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    def get_client_key(self, request: Request) -> str:
        """Extract client identifier from request"""
        # Priority order: API key > Client ID > IP address
        
        # Check for API key
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"apikey:{api_key[:16]}"
        
        # Check for client ID in body (for POST requests)
        if request.method == 'POST':
            # This would require caching the body, so use header instead
            client_id = request.headers.get('X-Client-ID')
            if client_id:
                return f"client:{client_id}"
        
        # Fallback to IP address
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            ip = forwarded_for.split(',')[0].strip()
        else:
            ip = request.client.host if request.client else 'unknown'
        
        return f"ip:{ip}"
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to request"""
        
        # Skip rate limiting for health check
        if request.url.path in ['/health', '/metrics', '/.well-known/agent.json']:
            return await call_next(request)
        
        client_key = self.get_client_key(request)
        allowed, info = await self.rate_limiter.is_allowed(client_key)
        
        if not allowed:
            return JSONResponse(
                {
                    "status": "error",
                    "error_type": "rate_limit_exceeded",
                    "message": "Rate limit exceeded. Please retry after the specified time.",
                    "retry_after": info.get('retry_after', 60),
                    "limit": self.rate_limiter.rate,
                    "period": self.rate_limiter.per
                },
                status_code=429,
                headers={
                    'X-RateLimit-Limit': str(self.rate_limiter.rate),
                    'X-RateLimit-Remaining': '0',
                    'X-RateLimit-Reset': str(info['reset']),
                    'Retry-After': str(info.get('retry_after', 60))
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(self.rate_limiter.rate)
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        response.headers['X-RateLimit-Reset'] = str(info['reset'])
        
        return response
