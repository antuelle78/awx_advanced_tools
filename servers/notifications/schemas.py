from pydantic import BaseModel


class ActivityStreamResponse(BaseModel):
    count: int
    next: str = None
    previous: str = None
