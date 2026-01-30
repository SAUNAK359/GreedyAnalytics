from sqlalchemy import Column, String
from analytics_llm.backend.storage.postgres import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True)
    name = Column(String)
