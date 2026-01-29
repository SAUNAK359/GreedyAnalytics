"""
Data source management for ingestion
"""
from typing import Dict, Any, List
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class DataSource:
    """Base data source class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.id = config.get("id", str(uuid.uuid4()))
        self.name = config.get("name", "Unnamed Source")
        self.type = config.get("type", "unknown")
    
    def schema(self) -> Dict[str, Any]:
        """Get data source schema"""
        return {"columns": [], "types": []}
    
    def sample(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample data"""
        return []
    
    def validate(self) -> bool:
        """Validate data source connection"""
        return True


class DataSourceManager:
    """Manages data sources for tenants"""
    
    def __init__(self):
        self.datasources = {}  # tenant_id -> list of datasources
    
    async def add_datasource(
        self, 
        tenant_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add new data source
        
        Args:
            tenant_id: Tenant identifier
            config: Data source configuration
            
        Returns:
            Created data source info
        """
        try:
            datasource_id = str(uuid.uuid4())
            
            datasource_info = {
                "id": datasource_id,
                "tenant_id": tenant_id,
                "name": config.get("name", "Unnamed"),
                "type": config.get("type", "unknown"),
                "config": config,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store datasource
            if tenant_id not in self.datasources:
                self.datasources[tenant_id] = []
            
            self.datasources[tenant_id].append(datasource_info)
            
            logger.info(f"Data source {datasource_id} added for tenant {tenant_id}")
            return datasource_info
            
        except Exception as e:
            logger.error(f"Failed to add data source: {e}")
            raise
    
    async def list_datasources(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        List all data sources for tenant
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            List of data sources
        """
        return self.datasources.get(tenant_id, [])
    
    async def get_datasource(
        self, 
        tenant_id: str, 
        datasource_id: str
    ) -> Dict[str, Any]:
        """Get specific data source"""
        sources = self.datasources.get(tenant_id, [])
        for source in sources:
            if source["id"] == datasource_id:
                return source
        return None
    
    async def remove_datasource(
        self, 
        tenant_id: str, 
        datasource_id: str
    ) -> bool:
        """Remove data source"""
        try:
            if tenant_id in self.datasources:
                self.datasources[tenant_id] = [
                    s for s in self.datasources[tenant_id] 
                    if s["id"] != datasource_id
                ]
                logger.info(f"Data source {datasource_id} removed")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove data source: {e}")
            return False
