from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import tasks, ai_assistance
from app.models.base import init_db, close_db

app = FastAPI(title="Task Prioritization App")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(
    ai_assistance.router,
    prefix="/api/v1/ai",
    tags=["ai-assistance"]
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Welcome to Task Prioritization API"} 