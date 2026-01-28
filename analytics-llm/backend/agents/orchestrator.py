from agents.query_agent import QueryAgent

def run_agent(question, data, context):
    agent = QueryAgent()
    reasoning = agent.reason(question, context)
    plan = agent.plan(reasoning)
    results = agent.execute(plan, data)
    return agent.reflect(results)
