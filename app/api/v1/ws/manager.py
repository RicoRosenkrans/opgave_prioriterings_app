from fastapi import WebSocket
from typing import Dict, Set
import logging
import json

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # client_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        # task_id -> Set[client_id]
        self.task_subscriptions: Dict[int, Set[int]] = {}
        
    async def connect(self, client_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Klient {client_id} forbundet")
        
    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            # Fjern klient fra alle task subscriptions
            for subscribers in self.task_subscriptions.values():
                subscribers.discard(client_id)
        logger.info(f"Klient {client_id} afbrudt")
        
    async def subscribe_to_task(self, client_id: int, task_id: int):
        if task_id not in self.task_subscriptions:
            self.task_subscriptions[task_id] = set()
        self.task_subscriptions[task_id].add(client_id)
        logger.info(f"Klient {client_id} subscribed til task {task_id}")
        
    async def unsubscribe_from_task(self, client_id: int, task_id: int):
        if task_id in self.task_subscriptions:
            self.task_subscriptions[task_id].discard(client_id)
        logger.info(f"Klient {client_id} unsubscribed fra task {task_id}")
        
    async def broadcast_task_update(self, task_id: int, update: dict):
        if task_id in self.task_subscriptions:
            for client_id in self.task_subscriptions[task_id]:
                if client_id in self.active_connections:
                    try:
                        await self.active_connections[client_id].send_json({
                            "type": "task_update",
                            "task_id": task_id,
                            **update
                        })
                    except Exception as e:
                        logger.error(f"Fejl ved broadcast til klient {client_id}: {str(e)}")
                        
    async def send_personal_message(self, client_id: int, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Fejl ved sending til klient {client_id}: {str(e)}") 