from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from app.models.task import Task
from app.ai.chains.status_report import StatusReportChain
from app.ai.chains.task_prioritization import TaskPrioritizationChain
from .manager import ConnectionManager
from typing import Dict, List
from pydantic import BaseModel

# Models for request/response dokumentation
class StatusRequest(BaseModel):
    """
    Request format for status updates
    """
    type: str = "status_request"
    tasks: List[Task]

    class Config:
        json_schema_extra = {
            "example": {
                "type": "status_request",
                "tasks": [{
                    "id": 1,
                    "title": "Implementer login",
                    "description": "Tilføj brugerautentifikation",
                    "status": "TODO",
                    "priority": "HIGH",
                    "deadline": "2024-02-10T12:00:00Z"
                }]
            }
        }

class PriorityRequest(BaseModel):
    """
    Request format for priority suggestions
    """
    type: str = "priority_request"
    task: Task

    class Config:
        json_schema_extra = {
            "example": {
                "type": "priority_request",
                "task": {
                    "id": 1,
                    "title": "Fix kritisk bug",
                    "description": "Systemet crasher ved store datamængder",
                    "status": "TODO",
                    "priority": "MEDIUM",
                    "deadline": "2024-02-15T16:00:00Z"
                }
            }
        }

class SubscribeRequest(BaseModel):
    """
    Request format for task subscriptions
    """
    type: str = "subscribe"
    task_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "type": "subscribe",
                "task_id": 1
            }
        }

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/dialog/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """
    WebSocket endpoint for real-time dialog og opdateringer.
    
    Understøtter følgende beskedtyper:
    - status_request: Anmod om statusrapport for en liste af opgaver
    - priority_request: Få forslag til prioritering af en opgave
    - subscribe: Abonner på opdateringer for en specifik opgave
    - unsubscribe: Afmeld abonnement på opgaveopdateringer

    Eksempel på brug:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/dialog/1');
    
    // Subscribe til en opgave
    ws.send(JSON.stringify({
        type: 'subscribe',
        task_id: 123
    }));
    
    // Anmod om prioritetsforslag
    ws.send(JSON.stringify({
        type: 'priority_request',
        task: {
            id: 123,
            title: 'Min opgave',
            description: 'Beskrivelse',
            status: 'TODO'
        }
    }));
    
    // Håndter svar
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Modtaget:', data);
    };
    ```
    """
    await manager.connect(client_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "subscribe":
                task_id = data.get("task_id")
                await manager.subscribe_to_task(client_id, task_id)
                await manager.send_personal_message(client_id, {
                    "type": "subscribed",
                    "task_id": task_id
                })
                
            elif message_type == "unsubscribe":
                task_id = data.get("task_id")
                await manager.unsubscribe_from_task(client_id, task_id)
                
            elif message_type == "status_request":
                chain = StatusReportChain()
                tasks = [Task(**task) for task in data.get("tasks", [])]
                report = await chain.generate_status_report(tasks)
                await manager.send_personal_message(client_id, {
                    "type": "status_response",
                    "report": report
                })
                
            elif message_type == "priority_request":
                chain = TaskPrioritizationChain()
                task = Task(**data.get("task", {}))
                suggestion = await chain.get_priority_suggestion(task)
                
                # Send prioritetsforslag til alle subscribers
                await manager.broadcast_task_update(task.id, {
                    "type": "priority_update",
                    "suggestion": suggestion
                })
                
            else:
                await manager.send_personal_message(client_id, {
                    "type": "error",
                    "message": "Ukendt beskedtype"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        
    except Exception as e:
        logger.error(f"Fejl i WebSocket forbindelse: {str(e)}")
        await manager.send_personal_message(client_id, {
            "type": "error",
            "message": "Der opstod en fejl i forbindelsen"
        })
        manager.disconnect(client_id) 