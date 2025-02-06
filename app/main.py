from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.base import init_db, close_db
from app.api.v1.api import api_router
from app.api.v1.ws.dialog import router as ws_router
from app.core.config import settings
import logging

app = FastAPI(title=settings.PROJECT_NAME)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Welcome to Task Prioritization API"} 