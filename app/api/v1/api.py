from fastapi import APIRouter
from app.api.v1.endpoints import tasks, ai_assistance

api_router = APIRouter()

# Inkluder alle endpoints
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)

api_router.include_router(
    ai_assistance.router,
    prefix="/ai",
    tags=["ai-assistance"]
) 