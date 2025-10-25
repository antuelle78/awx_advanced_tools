from pydantic import BaseModel


class MCPRequest(BaseModel):
    context_id: str | None = None
    platform: str
    action: str
    payload: dict

    class Config:
        arbitrary_types_allowed = True


class MCPResponse(BaseModel):
    context_id: str
    result: dict
