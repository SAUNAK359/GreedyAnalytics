ROLE_MATRIX = {
    "admin": {"deploy", "delete", "view", "edit"},
    "analyst": {"view", "edit"},
    "viewer": {"view"}
}

def authorize(role, action):
    return action in ROLE_MATRIX.get(role, set())
