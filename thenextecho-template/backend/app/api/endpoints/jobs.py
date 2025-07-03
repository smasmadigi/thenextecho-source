from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.crud import job as job_crud
from app.celery_worker import generation_pipeline_task

router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(job_in: JobCreate, db: AsyncSession = Depends(get_db)):
    new_job = await job_crud.create_new_job(db=db, theme=job_in.theme, model_name=job_in.model)
    generation_pipeline_task.delay(new_job.task_id)
    return new_job

@router.get("/", response_model=List[JobResponse])
async def read_jobs(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    jobs = await job_crud.get_all_jobs(db, skip=skip, limit=limit)
    return jobs

@router.post("/{task_id}/action/{action}")
async def job_action(task_id: str, action: str):
    if action == "approve":
        generation_pipeline_task.delay(task_id, resume=True)
        return {"message": "Étape approuvée, poursuite du pipeline."}
    elif action == "reroll":
        generation_pipeline_task.delay(task_id, reroll=True)
        return {"message": "Relance de l'étape demandée."}
    else:
        raise HTTPException(status_code=400, detail="Action non valide.")
