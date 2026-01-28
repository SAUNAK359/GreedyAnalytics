import jwt
from datetime import datetime, timedelta
from typing import Dict

# IMPORTANT:
# In production, load this from ENV or a secrets manager (Vault, AWS Secrets Manager)
JWT_SECRET = "CHANGE_ME_IN_PROD"
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_TTL_MIN = 60        # 1 hour
REFRESH_TOKEN_TTL_DAYS = 7       # 7 days


class JWTError(Exception):
    pass


def create_access_token(
    user_id: str,
    tenant_id: str,
    role: str,
    extra_claims: Dict = None
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
