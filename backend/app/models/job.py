from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SAEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    AWAITING_SCRIPT_APPROVAL = "AWAITING_SCRIPT_APPROVAL"
    SCRIPT_APPROVED = "SCRIPT_APPROVED"
    AUDIO_GENERATING = "AUDIO_GENERATING"
    AWAITING_AUDIO_APPROVAL = "AWAITING_AUDIO_APPROVAL"
    AUDIO_APPROVED = "AUDIO_APPROVED"
    COMPILING = "COMPILING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    theme = Column(String, nullable=False)
    status = Column(SAEnum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    artifacts = Column(JSON, default={})
    error_message = Column(String, nullable=True)
