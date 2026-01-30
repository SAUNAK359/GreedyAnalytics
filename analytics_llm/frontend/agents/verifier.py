from typing import Dict, Any


class VerifierAgent:
    def verify(self, plan: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        if result.get("error"):
            return {"valid": False, "reason": result["error"], "data": None}

        data = result.get("data")
        if data is None:
            return {"valid": False, "reason": "Empty result", "data": None}

        return {"valid": True, "reason": "ok", "data": data}
