from cryptography.fernet import Fernet
import hashlib
import base64
from src import config

def get_fernet() -> Fernet:
    """
    Initializes and returns a Fernet instance with a key derived from the app's SECRET_KEY.
    This ensures the key is always 32 bytes and URL-safe base64 encoded.
    """
    # Use SHA-256 to hash the secret key to ensure it's 32 bytes
    hasher = hashlib.sha256(config.SECRET_KEY.encode('utf-8'))
    key = base64.urlsafe_b64encode(hasher.digest())
    return Fernet(key)

def encrypt_key(api_key: str) -> bytes:
    """Encrypts an API key."""
    fernet = get_fernet()
    return fernet.encrypt(api_key.encode())

def decrypt_key(encrypted_key: bytes) -> str:
    """Decrypts an API key."""
    fernet = get_fernet()
    return fernet.decrypt(encrypted_key).decode()
