def run(payload):
    payload["model"] = "gemma"
    return {"response": "gemma-output", "confidence": 0.82}
