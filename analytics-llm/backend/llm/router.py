from llm.providers import gemma, openai
from core.cost_controller import estimate_cost

LLM_PRIORITY = [
    {"name": "gemma", "max_cost": 0.002},
    {"name": "openai", "max_cost": 0.02}
]

def route_llm(task, payload):
    for llm in LLM_PRIORITY:
        if estimate_cost(task, llm["name"]) <= llm["max_cost"]:
            try:
                if llm["name"] == "gemma":
                    return gemma.run(payload)
                if llm["name"] == "openai":
                    return openai.run(payload)
            except Exception:
                continue
    raise RuntimeError("All LLM providers failed")
