from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from app.models.job import JobStatus

class JobBase(BaseModel):
    theme: str
    
class JobCreate(JobBase):
    model: str 

class JobResponse(JobBase):
    id: int
    task_id: str
    status: JobStatus
    artifacts: dict[str, Any]
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True
