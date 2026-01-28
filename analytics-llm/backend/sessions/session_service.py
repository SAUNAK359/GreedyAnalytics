import uuid

def create_session(user_id, tenant_id):
    return {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "tenant_id": tenant_id
    }
