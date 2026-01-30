import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from analytics_llm.backend.core.config import settings

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM

ACCESS_TOKEN_TTL_MIN = settings.ACCESS_TOKEN_TTL_MIN
REFRESH_TOKEN_TTL_DAYS = settings.REFRESH_TOKEN_TTL_DAYS


class JWTError(Exception):
    pass


def create_access_token(
    user_id: str,
    tenant_id: str,
    role: str,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Short-lived token used by:
    - API
    - UI
    - Agents
    """
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_TTL_MIN),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(
    user_id: str,
    tenant_id: str
) -> str:
    """
    Long-lived token used only to mint new access tokens
    """
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Dict:
    """
    Used by:
    - API middleware
    - Streamlit UI
    - Agent orchestrator
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTError("Token expired")
    except jwt.InvalidTokenError:
        raise JWTError("Invalid token")


def is_access_token(payload: Dict) -> bool:
    return payload.get("type") == "access"


def is_refresh_token(payload: Dict) -> bool:
    return payload.get("type") == "refresh"
