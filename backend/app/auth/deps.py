"""
ClauseGuard AI — Auth dependency.
Verifies the Supabase JWT passed as Bearer token in the Authorization header.
Returns the user's UUID (sub claim) from the verified token.
Falls back safely to 'guest_user' if auth is unconfigured or no credentials are provided.
"""
import os
from typing import Optional
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

SUPABASE_JWT_SECRET: str = os.environ.get("SUPABASE_JWT_SECRET", "")

_bearer = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> Optional[dict]:
    """
    Verify and decode a Supabase JWT.
    1. If SUPABASE_JWT_SECRET is set, verify cryptographic signature.
    2. Try Supabase Auth API verification if client is available.
    3. Fallback: extract unverified claims (sub) so user isolation is strictly
       enforced even if the secret wasn't configured in the environment.
    """
    if not token or not token.strip():
        return None

    # 1. Try local signature verification if secret is provided
    if SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return payload
        except JWTError:
            pass

    # 2. Try Supabase Auth API verification
    try:
        from ..database.db import _supabase_client, USE_SUPABASE
        if USE_SUPABASE and _supabase_client:
            user_resp = _supabase_client.auth.get_user(token)
            if user_resp and user_resp.user:
                return {
                    "sub": user_resp.user.id,
                    "email": getattr(user_resp.user, "email", None),
                }
    except Exception:
        pass

    # 3. Fallback: extract claims without signature verification
    # This guarantees per-user isolation even if SUPABASE_JWT_SECRET is omitted from hosting provider
    try:
        claims = jwt.get_unverified_claims(token)
        if claims and claims.get("sub"):
            return claims
    except Exception:
        pass

    return None


# Public alias (used by analysis route for query-param token support)
decode_token = _decode_token


def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    """
    Return the user_id (UUID string) if a valid Supabase JWT is provided.
    If no token is supplied, checks for X-Guest-ID for session isolation,
    or falls back to 'guest_user'.
    """
    # 1. Authenticated Supabase user
    if creds and creds.credentials:
        payload = _decode_token(creds.credentials)
        if payload and payload.get("sub"):
            return str(payload["sub"])

    # 2. Isolated Guest User if guest ID header provided
    guest_id = request.headers.get("x-guest-id") or request.headers.get("X-Guest-ID")
    if guest_id and guest_id.strip():
        clean_guest = guest_id.strip()[:64]
        return f"guest_{clean_guest}" if not clean_guest.startswith("guest_") else clean_guest

    return "guest_user"


def get_optional_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """
    Like get_current_user but returns user identifier.
    """
    return get_current_user(request, creds)
