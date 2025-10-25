from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.adapters.token_auth import verify_token

router = APIRouter()

# Define routes here
