from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import jwt
from datetime import datetime, timedelta, UTC
from app.config import settings

router = APIRouter()
security = HTTPBasic()


def create_token(username: str) -> str:
    expire = datetime.now(UTC) + timedelta(hours=24)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


@router.post("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    # Simple authentication - in production, verify against AWX or a user database
    if credentials.username == "admin" and credentials.password == "password":
        token = create_token(credentials.username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
