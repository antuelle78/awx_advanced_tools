# auth token dependency
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from app.config import settings

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return sub
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
