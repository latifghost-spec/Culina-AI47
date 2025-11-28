import os
import jwt
from typing import Any
from fastapi import Header, HTTPException, Query


JWT_SECRET: str = str(os.getenv("JWT_SECRET", "dev-secret") or "dev-secret")
JWT_ALG: str = str(os.getenv("JWT_ALG", "HS256") or "HS256")


def require_jwt_role(required: str, authorization: str | None = Header(None)) -> str:
    """Validate the JWT and return the role.

    `authorization` may be the full header value (e.g. "Bearer <token>") or a
    raw token string. This keeps backwards compatibility with older clients that
    passed the token as a query param or raw value.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="unauthorized")

    # Accept either "Bearer <token>" or the raw token value
    if isinstance(authorization, str) and authorization.lower().startswith("bearer "):
        token = authorization.split(None, 1)[1]
    else:
        token = authorization

    try:
        payload: dict[str, Any] = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])  # type: ignore[arg-type]
    except Exception:
        raise HTTPException(status_code=401, detail="unauthorized")
    role = payload.get("role", "chef")
    if role != required and not (required == "manager" and role in ["admin", "manager"]):
        raise HTTPException(status_code=403, detail="forbidden")
    return role


def issue_mock_token(email: str, role: str) -> str:
    token = jwt.encode({"email": email, "role": role}, JWT_SECRET, algorithm=JWT_ALG)
    # PyJWT may return bytes in some versions; ensure we always return str
    if isinstance(token, bytes):
        token = token.decode()
    return token


def require_jwt_role_dep(required: str):
    """Return a dependency function that enforces the given role using the Authorization header.

    Use like: Depends(require_jwt_role_dep("manager"))
    """
    def dep(authorization: str | None = Header(None), authorization_q: str | None = Query(None)):
        # Prefer Authorization header; fall back to ?authorization=token for older clients
        auth_value = authorization if authorization is not None else authorization_q
        return require_jwt_role(required, auth_value)

    return dep
