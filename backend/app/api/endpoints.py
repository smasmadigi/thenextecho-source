from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
from .endpoints import jobs

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
router = APIRouter()
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # On garde la connexion ouverte
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Endpoint utilisé par Celery pour diffuser les mises à jour
@router.post("/broadcast_update")
async def broadcast_update(update: dict):
    await manager.broadcast(json.dumps(update))
    return {"message": "Update broadcasted"}
