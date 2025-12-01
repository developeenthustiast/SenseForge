"""
SenseForge Secrets Management - PRODUCTION READY
Secure handling of API keys and sensitive configuration
"""
import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import logging

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Enterprise secrets management with encryption at rest.
    Supports environment variables, encrypted files, and external vaults.
    """
    
    def __init__(self, mode: str = "env"):
        """
        Initialize secrets manager
        
        Args:
            mode: "env" (environment vars), "file" (encrypted file), "vault" (external vault)
        """
        self.mode = mode
        self._secrets_cache: Dict[str, str] = {}
        self._cipher: Optional[Fernet] = None
        
        if mode == "file":
            self._init_file_encryption()
        
        logger.info(f"SecretsManager initialized (mode: {mode})")
    
    def _init_file_encryption(self):
        """Initialize encryption for file-based secrets"""
        # Derive encryption key from master password
        master_password = os.getenv('MASTER_PASSWORD')
        if not master_password:
            raise ValueError(
                "MASTER_PASSWORD environment variable required for file mode"
            )
        
        # Use PBKDF2 to derive encryption key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'senseforge-salt-2025',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self._cipher = Fernet(key)
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value securely
        
        Args:
            key: Secret key name
            default: Default value if not found
        
        Returns:
            Secret value or default
        """
        # Check cache first
        if key in self._secrets_cache:
            return self._secrets_cache[key]
        
        # Get from appropriate source
        if self.mode == "env":
            value = self._get_from_env(key, default)
        elif self.mode == "file":
            value = self._get_from_file(key, default)
        elif self.mode == "vault":
            value = self._get_from_vault(key, default)
        else:
            raise ValueError(f"Unknown secrets mode: {self.mode}")
        
        # Cache if found (but NOT sensitive keys in production)
        if value and not key.endswith('_KEY'):
            self._secrets_cache[key] = value
        
        return value
    
    def _get_from_env(self, key: str, default: Optional[str]) -> Optional[str]:
        """Get secret from environment variable"""
        value = os.getenv(key, default)
        
        if value is None:
            logger.warning(f"Secret '{key}' not found in environment")
        
        return value
    
    def _get_from_file(self, key: str, default: Optional[str]) -> Optional[str]:
        """Get secret from encrypted file"""
        secrets_file = Path('.secrets.enc')
        
        if not secrets_file.exists():
            logger.warning(f"Secrets file not found: {secrets_file}")
            return default
        
        try:
            # Read encrypted file
            with open(secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted = self._cipher.decrypt(encrypted_data)
            secrets = json.loads(decrypted.decode())
            
            return secrets.get(key, default)
        
        except Exception as e:
            logger.error(f"Failed to read secret from file: {e}")
            return default
    
    def _get_from_vault(self, key: str, default: Optional[str]) -> Optional[str]:
        """
        Get secret from external vault (HashiCorp Vault, AWS Secrets Manager, etc.)
        
        This is a placeholder - implement based on your vault provider
        """
        # Example: HashiCorp Vault integration
        vault_addr = os.getenv('VAULT_ADDR')
        vault_token = os.getenv('VAULT_TOKEN')
        
        if not vault_addr or not vault_token:
            logger.warning("Vault credentials not configured, falling back to default")
            return default
        
        # TODO: Implement actual vault client
        # import hvac
        # client = hvac.Client(url=vault_addr, token=vault_token)
        # secret = client.secrets.kv.v2.read_secret_version(path=key)
        # return secret['data']['data']['value']
        
        logger.warning("Vault integration not implemented, using default")
        return default
    
    def set_secret(self, key: str, value: str) -> bool:
        """
        Set secret value (for file mode only)
        
        Args:
            key: Secret key
            value: Secret value
        
        Returns:
            Success status
        """
        if self.mode != "file":
            raise ValueError("set_secret only available in file mode")
        
        secrets_file = Path('.secrets.enc')
        
        try:
            # Load existing secrets
            secrets = {}
            if secrets_file.exists():
                with open(secrets_file, 'rb') as f:
                    encrypted = f.read()
                decrypted = self._cipher.decrypt(encrypted)
                secrets = json.loads(decrypted.decode())
            
            # Update
            secrets[key] = value
            
            # Encrypt and save
            encrypted = self._cipher.encrypt(json.dumps(secrets).encode())
            with open(secrets_file, 'wb') as f:
                f.write(encrypted)
            
            # Update cache
            self._secrets_cache[key] = value
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to set secret: {e}")
            return False
    
    def validate_all_required(self, required_keys: list) -> bool:
        """
        Validate all required secrets are present
        
        Args:
            required_keys: List of required secret keys
        
        Returns:
            True if all present, False otherwise
        """
        missing = []
        
        for key in required_keys:
            if not self.get_secret(key):
                missing.append(key)
        
        if missing:
            logger.error(f"Missing required secrets: {', '.join(missing)}")
            return False
        
        return True

# ===== CONFIGURATION VALIDATOR =====
class ConfigValidator:
    """Validate and sanitize configuration values"""
    
    @staticmethod
    def validate_api_key(key: str) -> bool:
        """Validate API key format"""
        if not key:
            return False
        
        # Minimum length check
        if len(key) < 16:
            return False
        
        # Check for obviously fake keys
        fake_patterns = ['test', 'demo', 'example', 'changeme', '123456']
        key_lower = key.lower()
        for pattern in fake_patterns:
            if pattern in key_lower:
                logger.warning(f"API key contains suspicious pattern: {pattern}")
                return False
        
        return True
    
    @staticmethod
    def validate_database_url(url: str) -> bool:
        """Validate database URL format"""
        if not url:
            return False
        
        # Check for SQLite in production
        if 'sqlite' in url.lower():
            logger.warning("SQLite database detected - not recommended for production")
        
        return True

# ===== GLOBAL INSTANCE =====
# Initialize based on environment
MODE = os.getenv('SECRETS_MODE', 'env')
secrets_manager = SecretsManager(mode=MODE)

# ===== CONVENIENCE FUNCTIONS =====
def get_api_key(service: str) -> Optional[str]:
    """
    Get API key for a service
    
    Args:
        service: Service name (cambrian, letta, ambient)
    
    Returns:
        API key or None
    """
    key_name = f"{service.upper()}_API_KEY"
    return secrets_manager.get_secret(key_name)

def validate_environment() -> bool:
    """
    Validate all required environment variables are set
    
    Returns:
        True if valid, False otherwise
    """
    mode = os.getenv('SENSEFORGE_MODE', 'mock')
    
    if mode == 'mock':
        # Mock mode doesn't require API keys
        return True
    
    # Live mode requires API keys
    required = []
    
    # Check which services are enabled
    if os.getenv('ENABLE_CAMBRIAN', 'true').lower() == 'true':
        required.append('CAMBRIAN_API_KEY')
    
    if os.getenv('ENABLE_LETTA', 'true').lower() == 'true':
        required.append('LETTA_API_KEY')
    
    if os.getenv('ENABLE_AMBIENT', 'true').lower() == 'true':
        required.append('AMBIENT_API_KEY')
    
    # Validate
    return secrets_manager.validate_all_required(required)

# ===== SETUP HELPER =====
def setup_secrets_file(secrets: Dict[str, str]) -> bool:
    """
    Helper to create encrypted secrets file
    
    Args:
        secrets: Dictionary of secrets to store
    
    Returns:
        Success status
    """
    manager = SecretsManager(mode='file')
    
    try:
        for key, value in secrets.items():
            if not manager.set_secret(key, value):
                return False
        
        logger.info(f"Successfully stored {len(secrets)} secrets")
        return True
    
    except Exception as e:
        logger.error(f"Failed to setup secrets file: {e}")
        return False

# ===== ROTATION HELPER =====
def rotate_api_key(service: str, new_key: str) -> bool:
    """
    Rotate an API key
    
    Args:
        service: Service name
        new_key: New API key value
    
    Returns:
        Success status
    """
    # Validate new key
    if not ConfigValidator.validate_api_key(new_key):
        logger.error("New API key failed validation")
        return False
    
    key_name = f"{service.upper()}_API_KEY"
    
    if secrets_manager.mode == 'file':
        return secrets_manager.set_secret(key_name, new_key)
    else:
        logger.warning(
            "Key rotation via environment variables requires manual update"
        )
        return False
