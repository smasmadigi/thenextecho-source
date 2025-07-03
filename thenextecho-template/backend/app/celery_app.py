from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier .env à la racine du dossier `backend`
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
    include=['app.celery_worker']
)

celery_app.conf.update(
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

# Tâche planifiée
celery_app.conf.beat_schedule = {
    'discovery-agent-every-day': {
        'task': 'app.celery_worker.discovery_agent_task',
        'schedule': crontab(hour=3, minute=0),
    },
}
