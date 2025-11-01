from pydantic import BaseModel


class PingResponse(BaseModel):
    version: str
    active_node: str = None
