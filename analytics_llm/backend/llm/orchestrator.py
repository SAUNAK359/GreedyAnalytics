from analytics_llm.backend.core.cost_controller import choose_temperature

def run_llm(task, payload):
    temp = choose_temperature(task)
    payload["temperature"] = temp
    return payload
