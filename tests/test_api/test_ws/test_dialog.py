import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.task import Task, TaskStatus, TaskPriority
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock

@pytest.fixture
def mock_task():
    return Task(
        id=1,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        deadline=datetime.now(timezone.utc)
    )

def test_websocket_connection():
    with TestClient(app).websocket_connect("/ws/dialog/1") as websocket:
        # Test forbindelse
        data = {"type": "ping"}
        websocket.send_json(data)
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "Ukendt beskedtype" in response["message"]

@pytest.mark.asyncio
async def test_status_request():
    task = Task(
        id=1,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        deadline=datetime.now(timezone.utc).isoformat()
    )
    
    with TestClient(app).websocket_connect("/ws/dialog/1") as websocket:
        # Send status request
        data = {
            "type": "status_request",
            "tasks": [task.dict()]
        }
        websocket.send_json(data)
        
        # Modtag og verificer response
        response = websocket.receive_json()
        assert response["type"] == "status_response"
        assert "report" in response
        assert isinstance(response["report"], str)

@pytest.mark.asyncio
async def test_priority_request():
    task = Task(
        id=1,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        deadline=datetime.now(timezone.utc)
    )
    
    with TestClient(app).websocket_connect("/ws/dialog/1") as websocket:
        # Send priority request
        data = {
            "type": "priority_request",
            "task": task.dict()
        }
        websocket.send_json(data)
        
        # Modtag og verificer response
        response = websocket.receive_json()
        assert response["type"] == "priority_response"
        assert "suggestion" in response
        assert "suggested_priority" in response["suggestion"]
        assert "reasoning" in response["suggestion"]

@pytest.mark.asyncio
async def test_subscribe_to_task():
    with TestClient(app).websocket_connect("/ws/dialog/1") as websocket:
        task_id = 100
        websocket.send_json({
            "type": "subscribe",
            "task_id": task_id
        })
        
        response = websocket.receive_json()
        assert response["type"] == "subscribed"
        assert response["task_id"] == task_id

@pytest.mark.asyncio
async def test_unsubscribe_from_task():
    with TestClient(app).websocket_connect("/ws/dialog/1") as websocket:
        task_id = 100
        # Først subscribe
        websocket.send_json({
            "type": "subscribe",
            "task_id": task_id
        })
        websocket.receive_json()  # Ignorer subscribe response
        
        # Så unsubscribe
        websocket.send_json({
            "type": "unsubscribe",
            "task_id": task_id
        })
        
        # Send en task update og verificer at vi ikke modtager den
        with patch('app.api.v1.ws.dialog.TaskPrioritizationChain') as mock_chain:
            mock_chain.return_value.get_priority_suggestion.return_value = {
                "suggested_priority": "HIGH",
                "reasoning": "Test"
            }
            
            websocket.send_json({
                "type": "priority_request",
                "task": {"id": task_id}
            })
            
            # Vi burde modtage en error besked da vi ikke er subscribed
            response = websocket.receive_json()
            assert response["type"] == "error"

@pytest.mark.asyncio
async def test_multiple_clients_receive_updates(mock_task):
    client1 = TestClient(app).websocket_connect("/ws/dialog/1")
    client2 = TestClient(app).websocket_connect("/ws/dialog/2")
    
    with client1 as ws1, client2 as ws2:
        # Begge klienter subscriber til samme task
        task_id = mock_task.id
        for ws in [ws1, ws2]:
            ws.send_json({
                "type": "subscribe",
                "task_id": task_id
            })
            ws.receive_json()  # Håndter subscribe response
        
        # Send priority request fra client1
        ws1.send_json({
            "type": "priority_request",
            "task": mock_task.dict()
        })
        
        # Begge klienter skulle modtage opdateringen
        for ws in [ws1, ws2]:
            response = ws.receive_json()
            assert response["type"] == "task_update"
            assert response["task_id"] == task_id
            assert "suggestion" in response

@pytest.mark.asyncio
async def test_connection_error_handling():
    with TestClient(app).websocket_connect("/ws/dialog/1") as websocket:
        with patch('app.ai.chains.task_prioritization.TaskPrioritizationChain.get_priority_suggestion',
                  side_effect=Exception("Test error")):
            websocket.send_json({
                "type": "priority_request",
                "task": {}
            })
            
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "fejl" in response["message"].lower() 