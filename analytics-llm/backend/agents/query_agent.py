class QueryAgent:

    def reason(self, question, context):
        return {
            "intent": "anomaly_analysis",
            "steps": ["slice", "aggregate", "compare"]
        }

    def plan(self, reasoning):
        return [
            {"tool": "data_slice", "params": {"last_hours": 24}},
            {"tool": "aggregate", "params": {"metric": "fraud_rate"}},
            {"tool": "compare", "params": {"baseline": "7d"}}
        ]

    def execute(self, plan, data):
        results = []
        for step in plan:
            results.append({"step": step["tool"], "result": "ok"})
        return results

    def reflect(self, results):
        return {
            "summary": "Fraud spike correlated with night hours",
            "confidence": 0.84
        }
