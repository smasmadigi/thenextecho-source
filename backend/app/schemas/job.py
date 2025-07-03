from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from app.models.job import JobStatus

class JobBase(BaseModel):
    theme: str
    
class JobCreate(JobBase):
    model: str # Le nom du modèle à utiliser

class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    artifacts: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None

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
