"""
Session memory store for chat history and context
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
from analytics_llm.backend.vectorstore.vectordb import store_vector, VectorStore

logger = logging.getLogger(__name__)


class SessionMemoryStore:
    """Manages user session memories and interactions"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.sessions = {}  # In-memory cache
    
    def add_interaction(
        self, 
        user_id: str, 
        query: str, 
        response: Dict[str, Any]
    ):
        """
        Add interaction to session memory
        
        Args:
            user_id: User identifier
            query: User query
            response: System response
        """
        try:
            # Store in vector database
            interaction_text = f"User: {query}\nAssistant: {response.get('answer', '')}" 
            store_vector(user_id, interaction_text)
            
            # Cache in memory
            if user_id not in self.sessions:
                self.sessions[user_id] = []
            
            self.sessions[user_id].append({
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "response": response
            })
            
            # Keep only last 50 interactions in memory
            if len(self.sessions[user_id]) > 50:
                self.sessions[user_id] = self.sessions[user_id][-50:]
            
            logger.info(f"Interaction stored for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
    
    def get_history(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get user's interaction history
        
        Args:
            user_id: User identifier
            limit: Maximum number of interactions to return
            
        Returns:
            List of interactions
        """
        try:
            history = self.sessions.get(user_id, [])
            return history[-limit:]
        except Exception as e:
            logger.error(f"Failed to retrieve history: {e}")
            return []
    
    def clear_session(self, user_id: str):
        """Clear session for user"""
        try:
            if user_id in self.sessions:
                del self.sessions[user_id]
            logger.info(f"Session cleared for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
    
    def get_session_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's session"""
        history = self.get_history(user_id)
        return {
            "user_id": user_id,
            "interaction_count": len(history),
            "first_interaction": history[0]["timestamp"] if history else None,
            "last_interaction": history[-1]["timestamp"] if history else None
        }


# Legacy function for backward compatibility
def save_chat(session_id, message):
    """Legacy function to save chat"""
    store_vector(session_id, message)
