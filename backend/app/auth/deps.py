"""Fail-closed authentication and server-issued, signed demo sessions."""
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import httpx

_bearer = HTTPBearer(auto_error=False)
_demo_secret = os.getenv('DEMO_SESSION_SECRET') or secrets.token_urlsafe(48)

def demo_enabled():
    return os.getenv('ALLOW_DEMO', 'false').lower() == 'true'

def issue_demo_session():
    if not demo_enabled():
        raise HTTPException(403, 'Demo sessions are disabled. Please sign in.')
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    token = jwt.encode({'sub': 'demo_' + str(uuid.uuid4()), 'aud': 'clauseguard-demo',
                        'iss': 'clauseguard', 'exp': expires}, _demo_secret, algorithm='HS256')
    return {'access_token': token, 'expires_at': expires.isoformat()}

@lru_cache(maxsize=1)
def _jwks(url):
    response = httpx.get(url + '/auth/v1/.well-known/jwks.json', timeout=10)
    response.raise_for_status()
    return response.json()

def _decode_token(token):
    try:
        if demo_enabled():
            try:
                return jwt.decode(token, _demo_secret, algorithms=['HS256'],
                    audience='clauseguard-demo', issuer='clauseguard',
                    options={'require_exp': True, 'require_sub': True})
            except JWTError:
                pass
        url = os.getenv('SUPABASE_URL', '').rstrip('/')
        if not url:
            return None
        header = jwt.get_unverified_header(token)
        if header.get('alg') == 'HS256':
            key = os.getenv('SUPABASE_JWT_SECRET')
            if not key:
                return None
            algorithms = ['HS256']
        elif header.get('alg') in ('ES256', 'RS256'):
            key = _jwks(url)
            if not any(k.get('kid') == header.get('kid') for k in key.get('keys', [])):
                _jwks.cache_clear()
                key = _jwks(url)
            algorithms = ['ES256', 'RS256']
        else:
            return None
        return jwt.decode(token, key, algorithms=algorithms, audience='authenticated',
            issuer=url + '/auth/v1', options={'require_exp': True, 'require_sub': True})
    except (JWTError, ValueError, httpx.HTTPError):
        return None

decode_token = _decode_token

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    payload = _decode_token(creds.credentials) if creds else None
    if not payload or not payload.get('sub'):
        raise HTTPException(401, 'Session expired or invalid. Sign in or start a new demo session.')
    return str(payload['sub'])

get_optional_user = get_current_user
