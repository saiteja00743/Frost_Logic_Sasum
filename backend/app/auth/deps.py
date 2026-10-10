"""
ClauseGuard AI — Auth dependency.
Verifies the Supabase JWT passed as Bearer token in the Authorization header.
Returns the user's UUID (sub claim) from the verified token.
Falls back safely to 'guest_user' if auth is unconfigured or no credentials are provided.
"""
import os
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

SUPABASE_JWT_SECRET: str = os.environ.get("SUPABASE_JWT_SECRET", "")

_bearer = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> Optional[dict]:
    """Verify and decode a Supabase JWT. Returns None if invalid or secret missing."""
    if not SUPABASE_JWT_SECRET:
        return None
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError:
        return None

# Public alias (used by analysis route for query-param token support)
decode_token = _decode_token


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    """
    Return the user_id (UUID string) if a valid Supabase JWT is provided.
    If no token is supplied or SUPABASE_JWT_SECRET is not configured,
    gracefully returns 'guest_user' so the application works seamlessly
    without mandatory external auth configuration.
    """
    if not creds or not creds.credentials:
        return "guest_user"

    payload = _decode_token(creds.credentials)
    if payload and payload.get("sub"):
        return payload["sub"]

    return "guest_user"


def get_optional_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """
    Like get_current_user but returns None or user identifier.
    """
    return get_current_user(creds)
