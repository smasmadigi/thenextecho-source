from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.job import Job, JobStatus
import uuid

async def get_job_by_task_id(db: AsyncSession, task_id: str):
    result = await db.execute(select(Job).filter(Job.task_id == task_id))
    return result.scalars().first()

async def get_all_jobs(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

async def create_new_job(db: AsyncSession, theme: str, model_name: str) -> Job:
    task_id = str(uuid.uuid4())
    initial_artifacts = {"model_name": model_name}
    db_job = Job(task_id=task_id, theme=theme, status=JobStatus.PENDING, artifacts=initial_artifacts)
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job

async def update_job_status(db: AsyncSession, task_id: str, status: JobStatus, error: Optional[str] = None):
    job = await get_job_by_task_id(db, task_id)
    if not job:
        return None
    job.status = status
    if error:
        job.error_message = error
    await db.commit()
    await db.refresh(job)
    return job

async def update_job_artifacts(db: AsyncSession, task_id: str, new_artifacts: dict):
    job = await get_job_by_task_id(db, task_id)
    if not job:
        return None
    # Pour JSON, il faut s'assurer que l'objet est mutable
    current_artifacts = dict(job.artifacts)
    current_artifacts.update(new_artifacts)
    job.artifacts = current_artifacts
    await db.commit()
    await db.refresh(job)
    return job
