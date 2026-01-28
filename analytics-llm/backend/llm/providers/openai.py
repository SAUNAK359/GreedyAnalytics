def run(payload):
    payload["model"] = "gpt-4o"
    return {"response": "openai-output", "confidence": 0.91}
