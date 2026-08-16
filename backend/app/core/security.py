import os
import time
import json
import base64
import hashlib
import secrets
import hmac
from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db

# Cryptographic secrets
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "skillbridge-production-secret-jwt-key-2026-auth-token")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days token validity


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


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(data_str: str) -> bytes:
    padding = "=" * (-len(data_str) % 4)
    return base64.urlsafe_b64decode((data_str + padding).encode("utf-8"))


def create_access_token(student_id: int, expires_delta_seconds: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    """
    Generate a verified, cryptographically signed HS256 JWT.
    Contains ONLY the unique student ID and standard claims (sub, iat, exp).
    Does NOT contain sensitive passwords or entire profile payloads.
    """
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(student_id),
        "student_id": int(student_id),
        "iat": now,
        "exp": now + expires_delta_seconds,
    }

    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verify_access_token(token: str) -> Optional[int]:
    """
    Verify the token signature and expiration.
    Returns the authenticated student_id (int) if valid, None if invalid, tampered, or expired.
    """
    if not token or not isinstance(token, str):
        return None

    clean_token = token.replace("Bearer ", "").strip()
    parts = clean_token.split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, signature_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()

    try:
        actual_sig = _base64url_decode(signature_b64)
    except Exception:
        return None

    if not hmac.compare_digest(expected_sig, actual_sig):
        return None  # Signature mismatch (tampered token)

    try:
        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

    # Check expiration
    now = int(time.time())
    if payload.get("exp") and payload["exp"] < now:
        return None  # Expired token

    student_id = payload.get("student_id") or payload.get("sub")
    if student_id is None:
        return None

    try:
        return int(student_id)
    except (ValueError, TypeError):
        return None


def get_current_student_id(authorization: Optional[str] = Header(None)) -> int:
    """
    FastAPI dependency: Extracts and cryptographically verifies the student ID
    from the Authorization: Bearer <token> header.
    Throws HTTP 401 Unauthorized if missing, expired, or invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student_id = verify_access_token(authorization)
    if not student_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return student_id


def get_optional_student_id(authorization: Optional[str] = Header(None)) -> Optional[int]:
    """FastAPI dependency: Optional token extraction for public/semi-public routes."""
    if not authorization:
        return None
    return verify_access_token(authorization)


def generate_session_token(student_id: int = 1) -> str:
    """Compatibility wrapper: generate signed JWT access token for student."""
    return create_access_token(student_id)

