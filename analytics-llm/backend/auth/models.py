from sqlalchemy import Column, String, DateTime
from storage.postgres import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    role = Column(String)
    tenant_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
