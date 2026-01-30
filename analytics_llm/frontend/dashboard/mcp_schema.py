from typing import List, Dict, Any
from pydantic import BaseModel, Field


class MCPComponent(BaseModel):
    id: str
    type: str
    data_source: str
    x: str | None = None
    y: str | None = None
    filters: Dict[str, Any] | None = None
    title: str | None = None


class MCPState(BaseModel):
    version: str = "v3"
    components: List[MCPComponent] = Field(default_factory=list)
    annotations: List[str] = Field(default_factory=list)
