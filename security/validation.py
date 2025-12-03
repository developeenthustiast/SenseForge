"""
SenseForge Input Validation & Sanitization - SECURITY HARDENED
Implements comprehensive XSS, SQL injection, and injection attack prevention
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import re
import html
import unicodedata
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ===== SANITIZATION ENGINE =====
class SecuritySanitizer:
    """
    Multi-layer sanitization for all user inputs
    """
    
    # Dangerous patterns to block
    FORBIDDEN_PATTERNS = [
        # SQL Injection
        r'(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bEXEC\b|\bUNION\b)',
        r'(--|;|\|\||&&)',
        # Command Injection
        r'(\$\(|\`|eval\(|exec\()',
        # XSS
        r'(<script|<iframe|<object|<embed|onerror|onload)',
        # Path Traversal
        r'(\.\./|\.\.\\)',
    ]
    
    # JavaScript event handlers to strip
    JS_EVENTS = [
        'onload', 'onerror', 'onclick', 'onmouseover', 'onmouseout',
        'onfocus', 'onblur', 'onchange', 'onsubmit', 'onkeydown',
        'onkeyup', 'onkeypress', 'ontouchstart', 'ontouchend'
    ]
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 10000) -> str:
        """
        Comprehensive text sanitization
        
        Args:
            text: Input text
            max_length: Maximum allowed length
        
        Returns:
            Sanitized text
        
        Raises:
            ValueError: If text contains forbidden patterns
        """
        if not text:
            return ""
        
        # Length check
        if len(text) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")
        
        # Unicode normalization (prevents homograph attacks)
        text = unicodedata.normalize('NFKC', text)
        
        # Check for forbidden patterns
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError(
                    f"Input contains forbidden pattern. Query rejected for security."
                )
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # HTML escape (basic XSS prevention)
        text = html.escape(text, quote=True)
        
        # Strip JavaScript event handlers
        for event in cls.JS_EVENTS:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(event), re.IGNORECASE)
            text = pattern.sub('', text)
        
        # Remove data URIs (can contain JavaScript)
        text = re.sub(r'data:[^,]*,', '', text, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        return text
    
    @classmethod
    def sanitize_html(cls, html_text: str) -> str:
        """
        Aggressive HTML sanitization using bleach
        
        Args:
            html_text: HTML input
        
        Returns:
            Sanitized HTML with no tags
        """
        try:
            import bleach
            
            # Strip ALL HTML tags
            clean = bleach.clean(
                html_text,
                tags=[],  # No tags allowed
                attributes={},
                strip=True,
                strip_comments=True
            )
            
            return clean
        
        except ImportError:
            logger.warning("bleach not installed, using fallback sanitization")
            # Fallback: strip all tags manually
            return re.sub(r'<[^>]+>', '', html_text)
    
    @classmethod
    def validate_proposal_id(cls, proposal_id: str) -> bool:
        """
        Validate proposal ID format
        
        Args:
            proposal_id: Proposal identifier
        
        Returns:
            True if valid format
        """
        # Format: PROP-<number>
        pattern = r'^PROP-\d{1,6}$'
        return bool(re.match(pattern, proposal_id))
    
    @classmethod
    def sanitize_metadata(cls, metadata: Dict) -> Dict:
        """
        Sanitize metadata dictionary
        
        Args:
            metadata: Metadata dict
        
        Returns:
            Sanitized metadata
        
        Raises:
            ValueError: If metadata too large or contains forbidden keys
        """
        if not metadata:
            return {}
        
        # Size check (prevent memory attacks)
        import sys
        size = sys.getsizeof(metadata)
        if size > 10 * 1024:  # 10KB limit
            raise ValueError("Metadata size exceeds limit (10KB)")
        
        # Forbidden keys (prevent credential leaks)
        forbidden_keys = {
            'password', 'secret', 'api_key', 'token', 'credential',
            'private_key', 'passphrase'
        }
        
        for key in metadata.keys():
            if any(forbidden in key.lower() for forbidden in forbidden_keys):
                raise ValueError(
                    f"Metadata cannot contain key: {key}"
                )
        
        # Sanitize all string values
        sanitized = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_text(value, max_length=1000)
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_metadata(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_text(str(v), max_length=1000) 
                    if isinstance(v, str) else v
                    for v in value[:100]  # Limit list size
                ]
            else:
                # Skip unsupported types
                logger.warning(f"Skipping metadata key {key} with unsupported type")
        
        return sanitized

# ===== REQUEST MODELS =====
class QueryRequest(BaseModel):
    """
    Validated and sanitized query request
    """
    query: str = Field(..., min_length=1, max_length=5000)
    proposal_id: Optional[str] = None
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('query')
    def sanitize_query(cls, v):
        """Sanitize query text"""
        return SecuritySanitizer.sanitize_text(v, max_length=5000)
    
    @validator('proposal_id')
    def validate_proposal(cls, v):
        """Validate proposal ID format"""
        if v is None:
            return v
        
        if not SecuritySanitizer.validate_proposal_id(v):
            raise ValueError(
                "Invalid proposal ID format. Expected: PROP-<number>"
            )
        
        return v
    
    @validator('context')
    def sanitize_context(cls, v):
        """Sanitize context"""
        if v is None:
            return v
        return SecuritySanitizer.sanitize_text(v, max_length=2000)
    
    @validator('metadata')
    def sanitize_metadata(cls, v):
        """Sanitize metadata"""
        if v is None:
            return {}
        return SecuritySanitizer.sanitize_metadata(v)
    
    class Config:
        # Prevent extra fields
        extra = 'forbid'

# ===== RESPONSE BUILDER =====
class SecureResponseBuilder:
    """
    Build secure API responses with appropriate information disclosure
    """
    
    @staticmethod
    def success_response(
        data: Any,
        request_id: str,
        include_debug: bool = False
    ) -> Dict:
        """
        Build success response
        
        Args:
            data: Response data
            request_id: Request identifier
            include_debug: Include debug information
        
        Returns:
            Response dictionary
        """
        import json
        from datetime import datetime as dt, date
        from uuid import UUID
        
        def datetime_handler(obj):
            if isinstance(obj, (dt, date)):
                return obj.isoformat()
            if isinstance(obj, UUID):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        # Convert any datetime objects to ISO format strings
        serializable_data = json.loads(json.dumps(data, default=datetime_handler))
        
        response = {
            'status': 'success',
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'data': serializable_data
        }
        
        if include_debug:
            response['debug'] = {
                'api_version': '2.0',
                'mode': 'development'
            }
        
        return response
    
    @staticmethod
    def error_response(
        error_type: str,
        message: str,
        request_id: str,
        details: Optional[Dict] = None,
        expose_details: bool = False
    ) -> Dict:
        """
        Build error response with controlled information disclosure
        
        Args:
            error_type: Error type identifier
            message: Error message
            request_id: Request identifier
            details: Additional error details
            expose_details: Whether to expose details (dev mode only)
        
        Returns:
            Error response dictionary
        """
        # In production, use generic error messages
        if not expose_details:
            safe_messages = {
                'validation_error': 'Invalid request parameters',
                'authentication_required': 'Authentication required',
                'invalid_api_key': 'Invalid credentials',
                'rate_limit_exceeded': 'Rate limit exceeded',
                'service_unavailable': 'Service temporarily unavailable',
                'internal_error': 'An error occurred'
            }
            
            message = safe_messages.get(error_type, 'An error occurred')
            details = None  # Never expose details in production
        
        response = {
            'status': 'error',
            'error_type': error_type,
            'message': message,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if details and expose_details:
            response['details'] = details
        
        return response

# ===== API KEY VALIDATOR =====
def validate_api_key(api_key: str, valid_keys: list) -> bool:
    """
    Validate API key with constant-time comparison
    
    Args:
        api_key: Key to validate
        valid_keys: List of valid keys
    
    Returns:
        True if valid
    """
    import hmac
    
    if not api_key or not valid_keys:
        return False
    
    # Constant-time comparison to prevent timing attacks
    for valid_key in valid_keys:
        if hmac.compare_digest(api_key, valid_key):
            return True
    
    return False

# ===== CONTENT SECURITY POLICY =====
def get_csp_header() -> str:
    """
    Get Content Security Policy header value
    
    Returns:
        CSP header string
    """
    policy = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self' https://api.anthropic.com",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ]
    
    return "; ".join(policy)

# ===== EXPORT =====
__all__ = [
    'SecuritySanitizer',
    'QueryRequest',
    'SecureResponseBuilder',
    'validate_api_key',
    'get_csp_header'
]
