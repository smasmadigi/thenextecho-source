from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json, logging

router = APIRouter()

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

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logging.info("Frontend client connected via WebSocket.")
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info("Frontend client disconnected.")

@router.post("/broadcast_update")
async def broadcast_update_from_worker(update: dict):
    await manager.broadcast(json.dumps(update))
    return {"status": "ok"}
