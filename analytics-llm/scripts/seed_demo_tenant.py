from storage.postgres import engine, SessionLocal, Base
from tenants.tenant_models import Tenant
from auth.models import User
from auth.auth_service import hash_password
import uuid

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    tenant_id = str(uuid.uuid4())

    tenant = Tenant(
        id=tenant_id,
        name="Demo Enterprise"
    )
    db.add(tenant)

    users = [
        User(
            id=str(uuid.uuid4()),
            email="admin@demo.com",
            role="admin",
            tenant_id=tenant_id,
            password=hash_password("admin123")
        ),
        User(
            id=str(uuid.uuid4()),
            email="analyst@demo.com",
            role="analyst",
            tenant_id=tenant_id,
            password=hash_password("analyst123")
        ),
        User(
            id=str(uuid.uuid4()),
            email="viewer@demo.com",
            role="viewer",
            tenant_id=tenant_id,
            password=hash_password("viewer123")
        )
    ]

    db.add_all(users)
    db.commit()
    db.close()

    print("✅ Demo tenant and users created")

if __name__ == "__main__":
    seed()
