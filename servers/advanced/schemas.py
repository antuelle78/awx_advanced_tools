from pydantic import BaseModel
from typing import Dict, Any, Optional


class CreateCredentialRequest(BaseModel):
    name: str
    credential_type: int
    inputs: Dict[str, Any]


class CreateWorkflowTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateWorkflowTemplateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class LaunchWorkflowRequest(BaseModel):
    extra_vars: Optional[Dict[str, Any]] = None
