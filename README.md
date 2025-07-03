# TheNextEcho - Titan Edition

Bienvenue dans TheNextEcho, une plateforme complète et évolutive pour la création de contenu vidéo automatisé par IA.

Ce dépôt contient le code source complet de l'application. Pour installer et déployer la plateforme sur une nouvelle machine, veuillez utiliser le script d'installation officiel (`install.sh`).

## Aperçu de l'Architecture

- **Frontend:** React + TypeScript + Vite + TailwindCSS + shadcn/ui
- **Backend:** FastAPI + Python
- **Tâches Asynchrones:** Celery
- **Messagerie & Cache:** Redis
- **Base de Données:** SQLAlchemy + SQLite + Alembic
- **Infrastructure:** Docker & Docker Compose
- **IA de Texte:** Ollama (local)
- **IA de Voix:** Coqui TTS (local)

Consultez le dossier `/docs` pour une documentation technique détaillée sur l'architecture, l'API et comment contribuer.

## Démarrage Rapide (pour les Développeurs)

Une fois l'application installée avec `install.sh`, voici les commandes pour la lancer :

1.  **Infrastructure:** `docker-compose up -d`
2.  **Workers :**
    - **Génération:** `cd backend && source venv/bin/activate && celery -A app.celery_worker worker --loglevel=info -P gevent`
    - **Veille:** `cd backend && source venv/bin/activate && celery -A app.celery_worker beat --loglevel=info`
3.  **Backend:** `cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
4.  **Frontend:** `cd frontend && npm run dev`
