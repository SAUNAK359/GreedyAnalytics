"""
Vector database for semantic search and memory
"""
import chromadb
from chromadb.config import Settings
import logging
from typing import Dict, Any, List, Optional, cast
from analytics_llm.backend.core.config import settings as app_settings
import os

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for chat history and semantic search"""
    
    def __init__(self):
        try:
            # Create persistent client
            persist_dir = app_settings.VECTOR_DB_PATH
            os.makedirs(persist_dir, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="chat_memory",
                metadata={"description": "User chat interactions and context"}
            )
            
            logger.info(f"✅ Vector store initialized at {persist_dir}")
            
        except Exception as e:
            logger.error(f"❌ Vector store initialization failed: {e}")
            # Fallback to in-memory
            self.client = chromadb.Client()
            self.collection = self.client.create_collection("chat_memory")
    
    def initialize(self):
        """Initialize vector store (for compatibility)"""
        pass
    
    def store_vector(
        self, 
        session_id: str, 
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store text vector in database
        
        Args:
            session_id: Session/user identifier
            text: Text to store
            metadata: Additional metadata
        """
        try:
            doc_id = f"{session_id}_{hash(text)}"
            
            meta = {"session_id": session_id}
            if metadata:
                meta.update(metadata)
            
            self.collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.debug(f"Vector stored for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to store vector: {e}")
    
    def retrieve(
        self, 
        session_id: str, 
        query: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve similar vectors
        
        Args:
            session_id: Session/user identifier
            query: Query text
            n_results: Number of results to return
            
        Returns:
            Query results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                where={"session_id": session_id},
                n_results=n_results
            )
            
            return cast(Dict[str, Any], results)
            
        except Exception as e:
            logger.error(f"Failed to retrieve vectors: {e}")
            return {"documents": [], "distances": [], "metadatas": []}
    
    def delete_session(self, session_id: str):
        """Delete all vectors for a session"""
        try:
            # Get all documents for session
            results = self.collection.get(
                where={"session_id": session_id}
            )
            
            if results and results.get("ids"):
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted vectors for session {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete session vectors: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_documents": 0}


# Global instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


# Legacy functions for backward compatibility
client = chromadb.Client()
collection = client.get_or_create_collection("chat_memory")

def store_vector(session_id, text):
    """Legacy function"""
    vs = get_vector_store()
    vs.store_vector(session_id, text)

def retrieve(session_id, query):
    """Legacy function"""
    vs = get_vector_store()
    return vs.retrieve(session_id, query)
