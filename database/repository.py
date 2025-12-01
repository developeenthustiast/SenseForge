#!/usr/bin/env python3
"""
SenseForge Security Setup Script
Initializes encryption keys, validates configuration, and checks for security issues
"""
import os
import sys
import subprocess
from pathlib import Path
from cryptography.fernet import Fernet
import secrets
import hashlib

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def generate_encryption_key():
    """Generate Fernet encryption key"""
    print_header("Generating Encryption Key")
    
    key = Fernet.generate_key()
    key_str = key.decode()
    
    print(f"Generated encryption key: {key_str}")
    print("\n⚠️  IMPORTANT: Store this key securely!")
    print("Add to .env file as:")
    print(f"ENCRYPTION_KEY={key_str}")
    
    return key_str

def generate_audit_key():
    """Generate audit trail signing key"""
    print_header("Generating Audit Signing Key")
    
    # Generate 256-bit random key
    key = secrets.token_hex(32)
    
    print(f"Generated audit key: {key}")
    print("\n⚠️  IMPORTANT: Store this key securely!")
    print("Add to .env file as:")
    print(f"AUDIT_KEY={key}")
    
    return key

def scan_for_secrets_in_git():
    """Scan git history for accidentally committed secrets"""
    print_header("Scanning Git History for Secrets")
    
    if not Path('.git').exists():
        print_warning("Not a git repository, skipping...")
        return
    
    # Patterns to search for
    patterns = [
        'api_key',
        'API_KEY',
        'secret',
        'SECRET',
        'password',
        'PASSWORD',
        'token',
        'TOKEN'
    ]
    
    print("Searching for potential secrets in git history...")
    
    found_secrets = False
    
    for pattern in patterns:
        try:
            result = subprocess.run(
                ['git', 'log', '-p', '--all', '-S', pattern],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Check if it's not just .env.example
                if '.env.example' not in result.stdout:
                    found_secrets = True
                    print_error(f"Found potential secret: '{pattern}'")
        
        except subprocess.TimeoutExpired:
            print_warning(f"Timeout scanning for: {pattern}")
        except Exception as e:
            print_warning(f"Error scanning for {pattern}: {e}")
    
    if found_secrets:
        print("\n❌ CRITICAL: Secrets found in git history!")
        print("Actions required:")
        print("1. Rotate all exposed keys immediately")
        print("2. Consider using BFG Repo-Cleaner to remove secrets")
        print("3. Force push cleaned history (coordinate with team)")
        print("4. Add pre-commit hooks to prevent future leaks")
    else:
        print_success("No secrets found in git history")

def validate_env_file():
    """Validate .env file configuration"""
    print_header("Validating Environment Configuration")
    
    env_path = Path('.env')
    
    if not env_path.exists():
        print_warning(".env file not found")
        print("Create .env from .env.example:")
        print("  cp .env.example .env")
        return False
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    mode = os.getenv('SENSEFORGE_MODE', 'mock')
    
    print(f"Mode: {mode}")
    
    # Required for production
    if mode == 'live':
        print("\nValidating production configuration...")
        
        required_vars = [
            'ENCRYPTION_KEY',
            'AUDIT_KEY',
            'CAMBRIAN_API_KEY',
            'LETTA_API_KEY',
            'AMBIENT_API_KEY',
        ]
        
        missing = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or value == '':
                missing.append(var)
            else:
                print_success(f"{var} configured")
        
        if missing:
            print_error(f"Missing required variables: {', '.join(missing)}")
            return False
        
        # Check authentication
        auth_enabled = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'
        if not auth_enabled:
            print_warning("ENABLE_AUTH is not set to 'true' in production mode")
        
        # Check HTTPS
        https_enabled = os.getenv('ENABLE_HTTPS_REDIRECT', 'false').lower() == 'true'
        if not https_enabled:
            print_warning("ENABLE_HTTPS_REDIRECT is not set to 'true' in production mode")
        
        # Check SSL certs
        ssl_key = os.getenv('SSL_KEYFILE')
        ssl_cert = os.getenv('SSL_CERTFILE')
        if not ssl_key or not ssl_cert:
            print_warning("SSL certificates not configured")
    
    print_success("Environment validation complete")
    return True

def check_dependencies():
    """Check security-critical dependencies"""
    print_header("Checking Security Dependencies")
    
    critical_packages = [
        'cryptography',
        'pydantic',
        'sqlalchemy',
        'bleach'
    ]
    
    try:
        import pip
        installed_packages = {pkg.key for pkg in pip.get_installed_distributions()}
    except:
        # Fallback method
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list'],
            capture_output=True,
            text=True
        )
        installed_packages = {
            line.split()[0].lower() 
            for line in result.stdout.split('\n') 
            if line
        }
    
    missing = []
    for package in critical_packages:
        if package not in installed_packages:
            missing.append(package)
        else:
            print_success(f"{package} installed")
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    return True

def run_security_scan():
    """Run security vulnerability scan"""
    print_header("Running Security Vulnerability Scan")
    
    try:
        # Check if safety is installed
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', 'safety'],
            capture_output=True
        )
        
        if result.returncode != 0:
            print_warning("'safety' not installed")
            print("Install with: pip install safety")
            return
        
        # Run safety check
        print("Scanning dependencies for known vulnerabilities...")
        result = subprocess.run(
            [sys.executable, '-m', 'safety', 'check', '--json'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("No known vulnerabilities found")
        else:
            print_error("Vulnerabilities detected!")
            print(result.stdout)
    
    except Exception as e:
        print_warning(f"Security scan failed: {e}")

def create_security_checklist():
    """Create deployment security checklist"""
    print_header("Production Deployment Checklist")
    
    checklist = """
    📋 SECURITY DEPLOYMENT CHECKLIST
    
    Configuration:
    [ ] SENSEFORGE_MODE set to 'live'
    [ ] ENABLE_AUTH set to 'true'
    [ ] ENABLE_HTTPS_REDIRECT set to 'true'
    [ ] ENCRYPTION_KEY generated and configured
    [ ] AUDIT_KEY generated and configured
    [ ] All API keys configured
    [ ] DATABASE_URL using PostgreSQL (not SQLite)
    [ ] REDIS_URL configured
    [ ] ALLOWED_HOSTS set to specific domains (not *)
    [ ] SSL_KEYFILE and SSL_CERTFILE configured
    [ ] RATE_LIMIT set appropriately
    
    Security:
    [ ] Git history scanned for secrets
    [ ] All default passwords changed
    [ ] API keys rotated
    [ ] Pre-commit hooks installed
    [ ] Security vulnerability scan passed
    [ ] Penetration test completed
    
    Infrastructure:
    [ ] Database backups configured
    [ ] Log rotation configured
    [ ] Monitoring/alerting enabled
    [ ] Firewall rules configured
    [ ] DDoS protection enabled
    [ ] WAF configured (if applicable)
    
    Testing:
    [ ] Health checks tested
    [ ] Load testing completed
    [ ] Failover testing completed
    [ ] Disaster recovery plan tested
    
    Documentation:
    [ ] Incident response plan created
    [ ] Runbook documented
    [ ] Contact information updated
    [ ] Security policies documented
    """
    
    print(checklist)
    
    # Save to file
    checklist_path = Path('SECURITY_CHECKLIST.md')
    with open(checklist_path, 'w') as f:
        f.write(checklist)
    
    print_success(f"Checklist saved to {checklist_path}")

def main():
    """Main setup routine"""
    print_header("🔒 SenseForge Security Setup")
    
    print("This script will help you set up security for SenseForge.\n")
    
    # Check dependencies
    if not check_dependencies():
        print_error("Dependency check failed")
        sys.exit(1)
    
    # Generate keys
    print("\n1. Generate encryption keys? (y/n): ", end='')
    if input().lower() == 'y':
        encryption_key = generate_encryption_key()
        audit_key = generate_audit_key()
        
        print("\n⚠️  Save these keys to your .env file now!")
        input("Press Enter when done...")
    
    # Validate environment
    print("\n2. Validate environment? (y/n): ", end='')
    if input().lower() == 'y':
        validate_env_file()
    
    # Scan git
    print("\n3. Scan git history for secrets? (y/n): ", end='')
    if input().lower() == 'y':
        scan_for_secrets_in_git()
    
    # Security scan
    print("\n4. Run security vulnerability scan? (y/n): ", end='')
    if input().lower() == 'y':
        run_security_scan()
    
    # Checklist
    print("\n5. Create deployment checklist? (y/n): ", end='')
    if input().lower() == 'y':
        create_security_checklist()
    
    print_header("Setup Complete!")
    print("Next steps:")
    print("1. Review and complete the security checklist")
    print("2. Test the application in mock mode")
    print("3. Deploy to staging environment")
    print("4. Run penetration tests")
    print("5. Deploy to production")

if __name__ == "__main__":
    main()
