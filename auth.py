"""OIDC JWT authentication boundary for sensitive driver-location endpoints."""

import os
from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

_bearer = HTTPBearer(auto_error=False)


def auth_required() -> bool:
    """Return whether authentication is enforced for sensitive endpoints."""
    return os.getenv("AUTH_REQUIRED", "false").strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=4)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def verify_bearer_token(token: str) -> dict[str, Any]:
    """Verify an RS256 OIDC/Cognito JWT using issuer JWKS and configured audience."""
    issuer = os.getenv("AUTH_ISSUER", "").rstrip("/")
    audience = os.getenv("AUTH_AUDIENCE", "")
    token_use = os.getenv("AUTH_TOKEN_USE", "access")

    if not issuer or not audience:
        raise RuntimeError("AUTH_ISSUER and AUTH_AUDIENCE are required when AUTH_REQUIRED=true")

    jwks_url = os.getenv("AUTH_JWKS_URL") or f"{issuer}/.well-known/jwks.json"
    signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)

    try:
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    claimed_audience = claims.get("aud") or claims.get("client_id")
    if claimed_audience != audience:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token audience is not authorized.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_use and claims.get("token_use") not in {None, token_use}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token type is not authorized.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims


async def require_authenticated_request(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any] | None:
    """Require a valid bearer token only when AUTH_REQUIRED is enabled."""
    if not auth_required():
        return None

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_bearer_token(credentials.credentials)
