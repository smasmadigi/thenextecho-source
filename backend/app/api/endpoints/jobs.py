from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.crud import job as job_crud
from app.celery_worker import generation_pipeline_task

router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(job_in: JobCreate, db: AsyncSession = Depends(get_db)):
    """
    Crée un nouveau job et lance la première étape du pipeline.
    """
    new_job = await job_crud.create_new_job(db=db, theme=job_in.theme, model_name=job_in.model)
    
    # Lance la tâche Celery pour démarrer le pipeline
    generation_pipeline_task.delay(new_job.task_id)

    return new_job

@router.get("/", response_model=List[JobResponse])
async def read_jobs(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    Récupère une liste de tous les jobs.
    """
    jobs = await job_crud.get_all_jobs(db, skip=skip, limit=limit)
    return jobs

@router.post("/{task_id}/approve_step")
async def approve_job_step(task_id: str):
    """
    Approuve l'étape en cours et lance la suivante.
    """
    generation_pipeline_task.delay(task_id, resume=True)
    return {"message": "Étape approuvée, poursuite du pipeline."}

@router.post("/{task_id}/reroll_step")
async def reroll_job_step(task_id: str, db: AsyncSession = Depends(get_db)):
    """
    Relance la dernière étape en échec ou en attente.
    """
    job = await job_crud.get_job_by_task_id(db, task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")

    # On ne relance que l'étape précédente. On passe le job actuel à la tâche
    generation_pipeline_task.delay(job.task_id, reroll=True)
    return {"message": "Relance de l'étape demandée."}

