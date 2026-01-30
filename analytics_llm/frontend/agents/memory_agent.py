from typing import Dict, Any


class MemoryAgent:
    def remember(self, memory: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
        memory[key] = value
        return memory
