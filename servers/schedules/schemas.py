"""Pydantic schemas for Schedules Management server."""
from pydantic import BaseModel
from typing import Optional

class CreateScheduleRequest(BaseModel):
    name: str
    rrule: str
    job_template_id: int

class UpdateScheduleRequest(BaseModel):
    name: Optional[str] = None
    rrule: Optional[str] = None
    enabled: Optional[bool] = None
