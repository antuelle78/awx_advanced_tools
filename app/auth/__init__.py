from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import token_auth

router = APIRouter()

# Define routes here
