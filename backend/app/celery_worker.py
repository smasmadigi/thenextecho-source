from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.job import Job, JobStatus
from app.crud import job as job_crud
import asyncio
import requests
import logging

def update_status_sync(task_id: str, step_info: dict):
    payload = {"type": "status", "task_id": task_id, "data": step_info}
    try:
        requests.post("http://localhost:8000/api/v1/broadcast_update", json=payload, timeout=2)
    except requests.exceptions.RequestException:
        logging.warning("Impossible de notifier le frontend.")

async def update_db_and_broadcast(task_id, status, artifacts=None, error=None):
    async with SessionLocal() as db:
        if artifacts:
            await job_crud.update_job_artifacts(db, task_id, artifacts)
        
        job = await job_crud.update_job_status(db, task_id, status, error)
        if job:
            update_status_sync(task_id, {
                "status": job.status.value,
                "artifacts": job.artifacts,
                "error": job.error_message
            })

@celery_app.task
def generation_pipeline_task(task_id: str, resume: bool = False, reroll: bool = False):
    loop = asyncio.get_event_loop()
    
    async def pipeline():
        job = await job_crud.get_job_by_task_id(SessionLocal(), task_id)
        if not job:
            return

        current_status = job.status

        # Déterminer quelle étape lancer
        if reroll:
            # La logique de reroll peut être complexe, pour l'instant on reprend
            pass 
        elif resume:
            if current_status == JobStatus.AWAITING_SCRIPT_APPROVAL:
                current_status = JobStatus.SCRIPT_APPROVED
            elif current_status == JobStatus.AWAITING_AUDIO_APPROVAL:
                current_status = JobStatus.AUDIO_APPROVED

        # --- MACHINE À ÉTATS DU PIPELINE ---
        
        # Étape 1: Écriture du script
        if current_status == JobStatus.PENDING:
            await update_db_and_broadcast(task_id, JobStatus.SCRIPT_WRITING)
            # Logique pour écrire le script, puis mise à jour
            script_result = "Ceci est un script généré par IA." # Dummy result
            await update_db_and_broadcast(
                task_id, 
                JobStatus.AWAITING_SCRIPT_APPROVAL,
                artifacts={"script": script_result}
            )

        # Étape 2: Génération Audio
        elif current_status == JobStatus.SCRIPT_APPROVED:
            await update_db_and_broadcast(task_id, JobStatus.AUDIO_GENERATING)
            # Logique de génération audio
            audio_path = "/path/to/generated_audio.mp3" # Dummy result
            await update_db_and_broadcast(
                task_id,
                JobStatus.AWAITING_AUDIO_APPROVAL,
                artifacts={"audio_path": audio_path}
            )
        # etc... pour les autres étapes

    loop.run_until_complete(pipeline())


@celery_app.task
def discovery_agent_task():
    # Placeholder pour l'agent de veille
    print("Agent de découverte : recherche de nouveaux modèles IA...")
    # 1. Scrapper des sources (Hugging Face, etc.)
    # 2. Si un nouveau modèle est trouvé et intéressant, l'ajouter à la DB
    # 3. Envoyer une notification WebSocket
    update_status_sync("discovery_agent", {"message": "Nouveau modèle 'super-llama-3000' découvert !"})
