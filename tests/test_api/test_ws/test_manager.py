import pytest
from unittest.mock import AsyncMock, MagicMock
from app.api.v1.ws.manager import ConnectionManager

@pytest.fixture
def mock_websocket():
    websocket = AsyncMock()
    websocket.send_json = AsyncMock()
    return websocket

@pytest.fixture
def manager():
    return ConnectionManager()

@pytest.mark.asyncio
async def test_connect(manager, mock_websocket):
    client_id = 1
    await manager.connect(client_id, mock_websocket)
    
    assert client_id in manager.active_connections
    assert manager.active_connections[client_id] == mock_websocket
    mock_websocket.accept.assert_called_once()

@pytest.mark.asyncio
async def test_disconnect(manager, mock_websocket):
    client_id = 1
    await manager.connect(client_id, mock_websocket)
    manager.disconnect(client_id)
    
    assert client_id not in manager.active_connections
    # Tjek at klienten er fjernet fra alle subscriptions
    for subscribers in manager.task_subscriptions.values():
        assert client_id not in subscribers

@pytest.mark.asyncio
async def test_subscribe_to_task(manager, mock_websocket):
    client_id = 1
    task_id = 100
    await manager.connect(client_id, mock_websocket)
    await manager.subscribe_to_task(client_id, task_id)
    
    assert task_id in manager.task_subscriptions
    assert client_id in manager.task_subscriptions[task_id]

@pytest.mark.asyncio
async def test_unsubscribe_from_task(manager, mock_websocket):
    client_id = 1
    task_id = 100
    await manager.connect(client_id, mock_websocket)
    await manager.subscribe_to_task(client_id, task_id)
    await manager.unsubscribe_from_task(client_id, task_id)
    
    assert client_id not in manager.task_subscriptions[task_id]

@pytest.mark.asyncio
async def test_broadcast_task_update(manager, mock_websocket):
    client_id = 1
    task_id = 100
    update = {"status": "completed"}
    
    await manager.connect(client_id, mock_websocket)
    await manager.subscribe_to_task(client_id, task_id)
    await manager.broadcast_task_update(task_id, update)
    
    mock_websocket.send_json.assert_called_once_with({
        "type": "task_update",
        "task_id": task_id,
        **update
    })

@pytest.mark.asyncio
async def test_send_personal_message(manager, mock_websocket):
    client_id = 1
    message = {"type": "test", "content": "hello"}
    
    await manager.connect(client_id, mock_websocket)
    await manager.send_personal_message(client_id, message)
    
    mock_websocket.send_json.assert_called_once_with(message)

@pytest.mark.asyncio
async def test_broadcast_to_multiple_clients(manager):
    client1_ws = AsyncMock()
    client2_ws = AsyncMock()
    task_id = 100
    update = {"status": "in_progress"}
    
    await manager.connect(1, client1_ws)
    await manager.connect(2, client2_ws)
    await manager.subscribe_to_task(1, task_id)
    await manager.subscribe_to_task(2, task_id)
    
    await manager.broadcast_task_update(task_id, update)
    
    expected_message = {
        "type": "task_update",
        "task_id": task_id,
        **update
    }
    client1_ws.send_json.assert_called_once_with(expected_message)
    client2_ws.send_json.assert_called_once_with(expected_message) 