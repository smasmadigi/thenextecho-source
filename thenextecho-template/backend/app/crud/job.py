from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.job import Job, JobStatus
import uuid
from typing import Optional

async def get_job_by_task_id(db: AsyncSession, task_id: str) -> Optional[Job]:
    result = await db.execute(select(Job).filter(Job.task_id == task_id))
    return result.scalars().first()

async def get_all_jobs(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Job]:
    result = await db.execute(select(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_new_job(db: AsyncSession, theme: str, model_name: str) -> Job:
    task_id = str(uuid.uuid4())
    initial_artifacts = {"model_name": model_name}
    db_job = Job(task_id=task_id, theme=theme, status=JobStatus.PENDING, artifacts=initial_artifacts)
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job

async def update_job_status_and_artifacts(db: AsyncSession, task_id: str, status: JobStatus, artifacts: Optional[dict] = None, error: Optional[str] = None) -> Optional[Job]:
    job = await get_job_by_task_id(db, task_id)
    if not job:
        return None
    job.status = status
    if error:
        job.error_message = error
        job.status = JobStatus.FAILED
    if artifacts:
        current_artifacts = dict(job.artifacts)
        current_artifacts.update(artifacts)
        job.artifacts = current_artifacts
    
    await db.commit()
    await db.refresh(job)
    return job
