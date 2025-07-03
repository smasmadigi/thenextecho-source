from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.router import api_router
from .database import engine, Base

app = FastAPI(title="TheNextEcho API - Titan Edition", version="9.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to TheNextEcho API Titan Edition"}
