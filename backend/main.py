
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

app = FastAPI()

# --- RBAC Setup ---
roles = ["super_admin", "admin", "friend"]
fake_users_db = {
    "superadmin": {"username": "superadmin", "role": "super_admin"},
    "admin": {"username": "admin", "role": "admin"},
    "friend": {"username": "friend", "role": "friend"},
}

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    # Simulate token parsing: "fake-token-for-{role}"
    if token.startswith("fake-token-for-"):
        role = token.replace("fake-token-for-", "")
        for user in fake_users_db.values():
            if user["role"] == role:
                return user
    raise HTTPException(status_code=401, detail="Invalid token")

def require_role(*allowed_roles):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return role_checker

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Comics Endpoints ---
@app.get("/comics")
def get_comics(user=Depends(require_role("super_admin", "admin", "friend"))):
    # Placeholder: return fake comics
    return [{"title": "Example Comic"}]

# --- User Management Endpoints ---
from fastapi import Response

@app.post("/users")
def create_user(data: dict, user=Depends(get_current_user)):
    # Only super_admin can create admin
    if data.get("role") == "admin":
        if user["role"] != "super_admin":
            raise HTTPException(status_code=403, detail="Only super_admin can create admin")
        return Response(content='{"msg": "Admin created"}', status_code=201, media_type="application/json")
    # Admin can create friend users, but not super_admin
    if data.get("role") == "super_admin":
        raise HTTPException(status_code=403, detail="Cannot create super_admin")
    if user["role"] == "admin" and data.get("role") in ["friend"]:
        return Response(content='{"msg": "User created"}', status_code=201, media_type="application/json")
    raise HTTPException(status_code=403, detail="Forbidden")
