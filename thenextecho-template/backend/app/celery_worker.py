from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.job import JobStatus
from app.crud import job as job_crud
from app.tools.video_pipeline import run_pipeline_step
import asyncio
import requests
import logging

def broadcast_to_frontend(payload: dict):
    try:
        requests.post("http://localhost:8000/api/v1/broadcast_update", json=payload, timeout=2)
    except requests.exceptions.RequestException:
        logging.warning("Impossible de notifier le frontend.")

async def update_db_and_broadcast(task_id, status, artifacts=None, error=None):
    async with SessionLocal() as db:
        job = await job_crud.update_job_status_and_artifacts(db, task_id, status, artifacts, error)
        if job:
            broadcast_to_frontend({
                "type": "JOB_UPDATE",
                "data": {
                    "task_id": job.task_id,
                    "status": job.status.value,
                    "artifacts": job.artifacts,
                    "error_message": job.error_message,
                }
            })

@celery_app.task
def generation_pipeline_task(task_id: str, resume: bool = False, reroll: bool = False):
    loop = asyncio.get_event_loop()
    async def pipeline():
        async with SessionLocal() as db:
            job = await job_crud.get_job_by_task_id(db, task_id)
        if not job:
            return
        
        current_status = job.status
        if resume:
            if current_status == JobStatus.AWAITING_SCRIPT_APPROVAL: current_status = JobStatus.SCRIPT_APPROVED
            elif current_status == JobStatus.AWAITING_AUDIO_APPROVAL: current_status = JobStatus.AUDIO_APPROVED
        
        next_step, new_artifacts, error = await run_pipeline_step(current_status, job.theme, job.artifacts)
        
        await update_db_and_broadcast(task_id, next_step, new_artifacts, error)
    loop.run_until_complete(pipeline())

@celery_app.task
def discovery_agent_task():
    print("Agent de découverte...")
    broadcast_to_frontend({"type": "DISCOVERY", "data": {"message": "Nouveau modèle 'super-llama-3000' découvert !"}})
