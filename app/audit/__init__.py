from pydantic import BaseModel

class AuditLogEntry(BaseModel):
    user: str
    action: str
    platform: str
    request: dict
    response: dict | None = None
    error: str | None = None
    timestamp: str

    class Config:
        arbitrary_types_allowed = True
