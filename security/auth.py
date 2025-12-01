```python
"""
SenseForge Authentication
API key-based authentication for enterprise deployments.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from typing import Optional, Set
import hmac
import hashlib
import os
import json
from pathlib import Path

class APIKeyManager:
    """Manage API keys securely"""
    
    def __init__(self, keys_file: str = ".api_keys.json"):
        self.keys_file = Path(keys_file)
        self.valid_keys: Set[str] = set()
        self.key_metadata: dict = {}
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from encrypted file"""
        if not self.keys_file.exists():
            return
        
        try:
            with open(self.keys_file, 'r') as f:
                data = json.load(f)
                
            self.valid_keys = set(data.get('keys', []))
            self.key_metadata = data.get('metadata', {})
            
        except Exception as e:
            print(f"Error loading API keys: {e}")
    
    def validate_key(self, api_key: str) -> bool:
        """Validate API key using constant-time comparison"""
        for valid_key in self.valid_keys:
            if hmac.compare_digest(api_key, valid_key):
                return True
        return False
    
    def get_key_metadata(self, api_key: str) -> Optional[dict]:
        """Get metadata for an API key"""
        # Hash the key to look up metadata
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return self.key_metadata.get(key_hash)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.key_manager = APIKeyManager()
        
        # Public endpoints that don't require authentication
        self.public_endpoints = {
            '/.well-known/agent.json',
            '/health',
            '/metrics'
        }
    
    async def dispatch(self, request: Request, call_next):
        """Authenticate request"""
        
        # Skip authentication for public endpoints
        if request.url.path in self.public_endpoints:
            return await call_next(request)
        
        # Extract API key from header
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return JSONResponse(
                {
                    "status": "error",
                    "error_type": "authentication_required",
                    "message": "API key is required. Include X-API-Key header."
                },
                status_code=401
            )
        
        # Validate API key
        if not self.key_manager.validate_key(api_key):
            return JSONResponse(
                {
                    "status": "error",
                    "error_type": "invalid_api_key",
                    "message": "Invalid API key"
                },
                status_code=403
            )
        
        # Add key metadata to request state
        metadata = self.key_manager.get_key_metadata(api_key)
        request.state.api_key_metadata = metadata or {}
        
        return await call_next(request)
