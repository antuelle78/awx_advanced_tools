from pydantic import BaseModel
from typing import Dict, Any

class CreateCredentialRequest(BaseModel):
    name: str
    credential_type: int
    inputs: Dict[str, Any]
