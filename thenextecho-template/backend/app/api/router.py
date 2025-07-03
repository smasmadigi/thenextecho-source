from fastapi import APIRouter
from .endpoints import jobs, system, ws

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(ws.router) # Websocket router
