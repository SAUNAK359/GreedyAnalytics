"""
Agent orchestrator for complex query execution
Manages multi-step reasoning and tool usage
"""
from typing import Dict, Any, List, Optional
import logging
from analytics_llm.backend.llm.router import LLMRouter
from analytics_llm.backend.core.config import settings
from analytics_llm.backend.core.cost_controller import estimate_cost, select_optimal_model, cost_optimizer, estimate_tokens, token_budget_limiter
from analytics_llm.backend.vectorstore.vectordb import VectorStore
from analytics_llm.backend.sessions.memory_store import SessionMemoryStore
from analytics_llm.backend.agents.query_agent import QueryAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates AI agents for complex analytics tasks"""
    
    def __init__(self):
        self.llm_router = LLMRouter()
        self.vector_store = VectorStore()
        self.session_store = SessionMemoryStore()
        self.query_agent = QueryAgent()
    
    async def execute_query(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute analytics query with multi-step reasoning
        
        Args:
            query: User query
            context: Execution context (user_id, tenant_id, etc.)
            
        Returns:
            Query result with metadata
        """
        try:
            logger.info(f"Executing query for user {context.get('user_id')}: {query}")
            
            # Step 1: Retrieve relevant context from memory
            relevant_context = await self._get_relevant_context(
                query, 
                context.get('user_id')
            )
            
            # Step 2: Plan execution steps
            plan = await self._create_execution_plan(query, relevant_context)
            
            # Step 3: Execute plan
            result = await self._execute_plan(plan, context)
            
            # Step 4: Store result in memory
            await self._store_result(query, result, context.get('user_id'))
            
            return {
                "answer": result.get("answer"),
                "confidence": result.get("confidence", 0.8),
                "steps": plan,
                "metadata": {
                    "model": result.get("model"),
                    "tokens_used": result.get("tokens_used"),
                    "execution_time_ms": result.get("execution_time_ms")
                }
            }
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return {
                "answer": "I encountered an error processing your query. Please try again.",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _get_relevant_context(
        self, 
        query: str, 
        user_id: Optional[str]
    ) -> List[str]:
        """Retrieve relevant context from vector store"""
        try:
            if not user_id:
                return []
            results = self.vector_store.retrieve(user_id, query)
            if results and results.get('documents'):
                return results['documents'][0][:3]
            return []
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return []
    
    async def _create_execution_plan(
        self, 
        query: str, 
        context: List[str]
    ) -> List[Dict[str, Any]]:
        """Create execution plan for query"""
        return [
            {
                "step": 1,
                "action": "analyze_query",
                "description": f"Analyze and answer: {query}"
            }
        ]
    
    async def _execute_plan(
        self, 
        plan: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the planned steps"""
        try:
            step = plan[0]
            payload = {
                "prompt": step["description"],
                "temperature": 0.5,
                "max_tokens": min(settings.OPENAI_MAX_TOKENS, 1000)
            }
            tenant_id = context.get("tenant_id", "default")

            estimated_tokens = estimate_tokens(payload["prompt"]) + payload["max_tokens"]
            if not token_budget_limiter.allow(tenant_id, estimated_tokens, settings.MAX_TOKENS_PER_MIN):
                return {
                    "answer": "Token budget exceeded. Please retry later.",
                    "confidence": 0.0,
                    "error": "TOKEN_BUDGET_EXCEEDED"
                }

            selected_model = select_optimal_model(payload["prompt"])
            estimated_cost = estimate_cost(payload["prompt"], selected_model, estimated_tokens)
            if not cost_optimizer.check_budget(tenant_id, estimated_cost):
                return {
                    "answer": "Cost budget exceeded. Please retry later.",
                    "confidence": 0.0,
                    "error": "COST_BUDGET_EXCEEDED"
                }

            result = await self.llm_router.route_request(payload, context)
            cost_optimizer.update_usage(tenant_id, result.get("estimated_cost", estimated_cost))
            return {
                "answer": result.get("response"),
                "confidence": result.get("confidence"),
                "model": result.get("model"),
                "tokens_used": result.get("tokens_used"),
                "execution_time_ms": 100
            }
        except Exception as e:
            logger.error(f"Plan execution error: {e}")
            raise
    
    async def _store_result(
        self, 
        query: str, 
        result: Dict[str, Any], 
        user_id: Optional[str]
    ):
        """Store query result in vector memory"""
        try:
            if not user_id:
                return
            text = f"Query: {query}\\nAnswer: {result.get('answer')}"
            self.vector_store.store_vector(user_id, text)
            self.session_store.add_interaction(user_id, query, result)
        except Exception as e:
            logger.error(f"Result storage error: {e}")


# Legacy function for backward compatibility
def run_agent(question, data, context):
    """Legacy function"""
    orchestrator = AgentOrchestrator()
    import asyncio
    return asyncio.run(orchestrator.execute_query(question, context))
