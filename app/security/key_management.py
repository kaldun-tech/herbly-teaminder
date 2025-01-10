"""Key management and validation module"""
import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Constants
DEFAULT_DEV_KEY = 'dev-secret-key-CHANGE-IN-PRODUCTION'
DEFAULT_TEST_KEY = 'TEST-secret-key-NOT-FOR-PRODUCTION'
MIN_KEY_LENGTH = 32
KEY_ROTATION_DAYS = 90  # Rotate keys every 90 days
KEY_FILE = '.key_metadata'

logger = logging.getLogger(__name__)

class KeyValidationError(Exception):
    """Raised when key validation fails"""
    pass

class KeyRotationError(Exception):
    """Raised when key rotation fails"""
    pass

def validate_secret_key(key: str, env: str) -> bool:
    """
    Validate the secret key based on environment
    
    Args:
        key: The secret key to validate
        env: The environment ('development', 'testing', 'production')
    
    Returns:
        bool: True if valid, raises KeyValidationError otherwise
    """
    if not key or not isinstance(key, str):
        raise KeyValidationError("Secret key must be a non-empty string")

    # Check key length
    if len(key) < MIN_KEY_LENGTH:
        raise KeyValidationError(f"Secret key must be at least {MIN_KEY_LENGTH} characters long")

    # Production-specific checks
    if env == 'production':
        if key in [DEFAULT_DEV_KEY, DEFAULT_TEST_KEY]:
            raise KeyValidationError("Production cannot use default development or test keys")
        if 'dev' in key.lower() or 'test' in key.lower():
            raise KeyValidationError("Production key contains development/test indicators")
        
        # Check key rotation
        last_rotation = get_last_rotation()
        if last_rotation and (datetime.now() - last_rotation).days > KEY_ROTATION_DAYS:
            raise KeyValidationError(f"Secret key needs rotation (older than {KEY_ROTATION_DAYS} days)")

    # Development/Testing specific checks
    elif env in ['development', 'testing']:
        if env == 'development' and key != DEFAULT_DEV_KEY:
            logger.warning("Using non-default development key")
        elif env == 'testing' and key != DEFAULT_TEST_KEY:
            logger.warning("Using non-default test key")

    return True

def generate_secret_key() -> str:
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(48)  # Generates a 64-character key

def get_last_rotation() -> Optional[datetime]:
    """Get the date of the last key rotation"""
    try:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'r') as f:
                timestamp = f.read().strip()
                return datetime.fromisoformat(timestamp)
    except Exception as e:
        logger.error(f"Error reading key metadata: {e}")
    return None

def update_rotation_timestamp() -> None:
    """Update the key rotation timestamp"""
    try:
        with open(KEY_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        logger.error(f"Error updating key metadata: {e}")

def rotate_secret_key() -> Tuple[str, str]:
    """
    Generate a new secret key and return both old and new keys
    
    Returns:
        Tuple[str, str]: (old_key, new_key)
    """
    old_key = os.environ.get('SECRET_KEY', DEFAULT_DEV_KEY)
    new_key = generate_secret_key()
    
    # Update environment variable
    os.environ['SECRET_KEY'] = new_key
    
    # Update rotation timestamp
    update_rotation_timestamp()
    
    return old_key, new_key

def get_days_until_rotation() -> int:
    """Get the number of days until next required rotation"""
    last_rotation = get_last_rotation()
    if not last_rotation:
        return 0
    
    days_since = (datetime.now() - last_rotation).days
    return max(0, KEY_ROTATION_DAYS - days_since)
