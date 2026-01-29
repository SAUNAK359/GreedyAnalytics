from typing import Dict, Any


def apply_policy(data: Dict[str, Any], role: str) -> Dict[str, Any]:
    if role in {"admin", "analyst"}:
        return data

    redacted = {}
    for key, value in data.items():
        if "pii" in key.lower():
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted
