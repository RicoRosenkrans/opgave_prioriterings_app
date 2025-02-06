from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.models.base import init_db, close_db
from app.api.v1.api import api_router
from app.core.config import settings
from app.websocket.connection_manager import ConnectionManager

app = FastAPI(title=settings.PROJECT_NAME)
manager = ConnectionManager()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3004"],  # Tilføj alle dine frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except:
        await manager.disconnect(websocket)

# Include router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    print(f"Connecting to database: {settings.DATABASE_URL}")
    try:
        await init_db()
        print("Successfully connected to database and initialized tables")
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Welcome to Task Prioritization API"} 