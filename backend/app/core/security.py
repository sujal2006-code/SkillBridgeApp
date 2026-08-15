import hashlib
import secrets
import hmac
from typing import Optional


def hash_password(password: str) -> str:
    """
    Securely hash a plain text password using PBKDF2-HMAC-SHA256
    with a cryptographically random 16-byte salt and 100,000 iterations.
    Format: pbkdf2_sha256$<salt_hex>$<hash_hex>
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return f"pbkdf2_sha256${salt}${pw_hash}"


def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """
    Verify a plain password against the stored PBKDF2 hash using
    constant-time comparison to prevent timing attacks.
    """
    if not plain_password or not hashed_password:
        return False
    parts = hashed_password.split("$")
    if len(parts) != 3 or parts[0] != "pbkdf2_sha256":
        return False
    salt = parts[1]
    expected_hash = parts[2]
    calculated_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return hmac.compare_digest(expected_hash, calculated_hash)


def generate_session_token() -> str:
    """Generate a secure, URL-safe random session token for student authentication."""
    return f"sb_st_{secrets.token_urlsafe(32)}"
