
"""
Security Testing
Test authentication, validation, and rate limiting.
"""
import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from security.validation import QueryRequest, SecureResponseBuilder, validate_api_key
from security.rate_limiter import RateLimiter
import asyncio

class TestInputValidation:
    """Test input validation"""
    
    def test_valid_query(self):
        """Test valid query passes validation"""
        request = QueryRequest(
            query="Analyze risk for PROP-123",
            proposal_id="PROP-123"
        )
        assert request.query == "Analyze risk for PROP-123"
    
    def test_query_sanitization(self):
        """Test HTML escaping"""
        # The validation logic now rejects dangerous patterns instead of just escaping them
        with pytest.raises(ValueError, match="forbidden pattern"):
            QueryRequest(query="Test <script>alert('xss')</script>")
    
    def test_dangerous_pattern_rejection(self):
        """Test rejection of dangerous patterns"""
        with pytest.raises(ValueError, match="forbidden pattern"):
            QueryRequest(query="DROP TABLE predictions")
        
        with pytest.raises(ValueError, match="forbidden pattern"):
            QueryRequest(query="eval(malicious_code)")
    
    def test_proposal_id_format(self):
        """Test proposal ID format validation"""
        # Valid
        request = QueryRequest(query="test", proposal_id="PROP-123")
        assert request.proposal_id == "PROP-123"
        
        # Invalid
        with pytest.raises(ValueError):
            QueryRequest(query="test", proposal_id="invalid-format")
    
    def test_metadata_size_limit(self):
        """Test metadata size limits"""
        large_metadata = {"key": "x" * 20000}
        
        with pytest.raises(ValueError, match="exceeds maximum length"):
            QueryRequest(query="test", metadata=large_metadata)
    
    def test_forbidden_metadata_keys(self):
        """Test forbidden keys in metadata"""
        with pytest.raises(ValueError, match="cannot contain key"):
            QueryRequest(query="test", metadata={"password": "secret"})

class TestRateLimiting:
    """Test rate limiting"""
    
    def test_allows_within_limit(self):
        """Test allows requests within limit"""
        async def _test():
            limiter = RateLimiter(rate=10, per=1.0, storage='memory')
            
            for i in range(5):
                allowed, info = await limiter.is_allowed(f"client_{i}")
                assert allowed
                assert info['remaining'] >= 0
        
        asyncio.run(_test())
    
    def test_blocks_over_limit(self):
        """Test blocks requests over limit"""
        async def _test():
            limiter = RateLimiter(rate=2, per=1.0, storage='memory')
            
            client_key = "test_client"
            
            # First 2 should pass
            for i in range(2):
                allowed, _ = await limiter.is_allowed(client_key)
                assert allowed
            
            # 3rd should be blocked
            allowed, info = await limiter.is_allowed(client_key)
            assert not allowed
            assert info['remaining'] == 0
            assert 'retry_after' in info
            
        asyncio.run(_test())

class TestAPIKeyValidation:
    """Test API key validation"""
    
    def test_valid_key(self):
        """Test valid API key"""
        valid_keys = ['test-key-123456789']
        assert validate_api_key('test-key-123456789', valid_keys)
    
    def test_invalid_key(self):
        """Test invalid API key"""
        valid_keys = ['test-key-123456789']
        assert not validate_api_key('wrong-key', valid_keys)
    
    def test_constant_time_comparison(self):
        """Test timing attack resistance"""
        import time
        
        valid_keys = ['a' * 32]
        
        # Time comparison with matching prefix
        start = time.perf_counter()
        validate_api_key('a' * 31 + 'b', valid_keys)
        time_wrong = time.perf_counter() - start
        
        # Time comparison with no match
        start = time.perf_counter()
        validate_api_key('b' * 32, valid_keys)
        time_different = time.perf_counter() - start
        
        # Times should be similar (constant time)
        assert abs(time_wrong - time_different) < 0.001  # 1ms tolerance

class TestSecureResponses:
    """Test secure response building"""
    
    def test_success_response(self):
        """Test success response format"""
        response = SecureResponseBuilder.success_response(
            {"result": "test"},
            "req-123"
        )
        
        assert response['status'] == 'success'
        assert response['request_id'] == 'req-123'
        assert 'timestamp' in response
        assert response['data'] == {"result": "test"}
    
    def test_error_response_hides_details(self):
        """Test error details are hidden in production"""
        response = SecureResponseBuilder.error_response(
            error_type="test_error",
            message="Detailed error message",
            request_id="req-123",
            details={"stack": "sensitive info"},
            expose_details=False
        )
        
        assert response['message'] == "An error occurred"
        assert 'details' not in response
    
    def test_error_response_shows_details_in_dev(self):
        """Test error details shown in development"""
        response = SecureResponseBuilder.error_response(
            error_type="test_error",
            message="Detailed error message",
            request_id="req-123",
            details={"stack": "debug info"},
            expose_details=True
        )
        
        assert response['message'] == "Detailed error message"
        assert response['details'] == {"stack": "debug info"}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])



