"""
ClauseGuard AI — Auth dependency.
Verifies the Supabase JWT passed as Bearer token in the Authorization header.
Returns the user's UUID (sub claim) from the verified token.
"""
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

SUPABASE_JWT_SECRET: str = os.environ.get("SUPABASE_JWT_SECRET", "")

_bearer = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    """Verify and decode a Supabase JWT. Raises 401 on failure."""
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET not configured on server.",
        )
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Public alias (used by analysis route for query-param token support)
decode_token = _decode_token


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    """
    Require a valid Supabase JWT and return the user_id (UUID string).
    Raises 401 if the token is missing or invalid.
    """
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = _decode_token(creds.credentials)
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing user identifier.",
        )
    return user_id


def get_optional_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """
    Like get_current_user but returns None instead of raising if no token.
    Used for endpoints that work both authenticated and anonymous.
    """
    if not creds:
        return None
    try:
        payload = _decode_token(creds.credentials)
        return payload.get("sub")
    except HTTPException:
        return None
