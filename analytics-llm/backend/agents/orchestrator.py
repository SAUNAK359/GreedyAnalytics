"""
Agent orchestrator for complex query execution
Manages multi-step reasoning and tool usage
"""
from typing import Dict, Any, List
import logging
from llm.router import LLMRouter
from vectorstore.vectordb import VectorStore
from sessions.memory_store import SessionMemoryStore
from agents.query_agent import QueryAgent

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
        user_id: str
    ) -> List[str]:
        """Retrieve relevant context from vector store"""
        try:
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
    ) -> List[Dict[str, str]]:
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
        plan: List[Dict[str, str]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the planned steps"""
        try:
            step = plan[0]
            payload = {
                "prompt": step["description"],
                "temperature": 0.5,
                "max_tokens": 1000
            }
            result = await self.llm_router.route_request(payload, context)
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
        user_id: str
    ):
        """Store query result in vector memory"""
        try:
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
