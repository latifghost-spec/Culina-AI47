import os
import jwt
from fastapi import Header, HTTPException, Query


JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")


def require_jwt_role(required: str, authorization: str | None = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")
    token = authorization.split()[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="unauthorized")
    role = payload.get("role", "chef")
    if role != required and not (required == "manager" and role in ["admin", "manager"]):
        raise HTTPException(status_code=403, detail="forbidden")
    return role


def issue_mock_token(email: str, role: str) -> str:
    return jwt.encode({"email": email, "role": role}, JWT_SECRET, algorithm=JWT_ALG)


def require_jwt_role_dep(required: str):
    """Return a dependency function that enforces the given role using the Authorization header.

    Use like: Depends(require_jwt_role_dep("manager"))
    """
    def dep(authorization: str | None = Header(None), authorization_q: str | None = Query(None)):
        # Prefer Authorization header; fall back to ?authorization=token for older clients
        auth_value = authorization if authorization is not None else authorization_q
        return require_jwt_role(required, auth_value)

    return dep
