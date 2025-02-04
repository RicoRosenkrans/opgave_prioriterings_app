import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app.models.task import TaskPriority, TaskStatus

def test_create_task(client: TestClient):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": TaskPriority.HIGH.value,
        "status": TaskStatus.TODO.value,
        "deadline": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["priority"] == task_data["priority"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_task_invalid_data(client: TestClient):
    # Test med manglende påkrævet felt
    response = client.post("/api/v1/tasks/", json={})
    assert response.status_code == 422
    
    # Test med for lang titel
    response = client.post("/api/v1/tasks/", json={"title": "a" * 101})
    assert response.status_code == 422

def test_read_tasks(client: TestClient):
    # Opret nogle test tasks
    task_data = [
        {"title": "Task 1", "description": "Description 1"},
        {"title": "Task 2", "description": "Description 2"},
    ]
    
    for task in task_data:
        client.post("/api/v1/tasks/", json=task)
    
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 2
    assert any(task["title"] == "Task 1" for task in data)
    assert any(task["title"] == "Task 2" for task in data)

def test_read_task(client: TestClient):
    # Opret en test task
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]
    
    # Hent tasken
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]

def test_read_task_not_found(client: TestClient):
    response = client.get("/api/v1/tasks/999999")
    assert response.status_code == 404

def test_update_task(client: TestClient):
    # Opret en test task
    task_data = {
        "title": "Original Title",
        "description": "Original Description",
        "status": TaskStatus.TODO.value
    }
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]
    
    # Opdater tasken
    update_data = {
        "title": "Updated Title",
        "status": TaskStatus.IN_PROGRESS.value
    }
    response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["status"] == update_data["status"]
    assert data["description"] == task_data["description"]  # Uændret felt

def test_update_task_not_found(client: TestClient):
    response = client.put(
        "/api/v1/tasks/999999",
        json={"title": "Updated Title"}
    )
    assert response.status_code == 404

def test_delete_task(client: TestClient):
    # Opret en test task
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]
    
    # Slet tasken
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204
    
    # Verificer at tasken er slettet
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404

def test_delete_task_not_found(client: TestClient):
    response = client.delete("/api/v1/tasks/999999")
    assert response.status_code == 404

@pytest.mark.parametrize("priority", list(TaskPriority))
def test_create_task_with_priority(client: TestClient, priority: TaskPriority):
    task_data = {
        "title": f"Task with {priority.value} priority",
        "priority": priority.value
    }
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201
    assert response.json()["priority"] == priority.value

@pytest.mark.parametrize("status", list(TaskStatus))
def test_create_task_with_status(client: TestClient, status: TaskStatus):
    task_data = {
        "title": f"Task with {status.value} status",
        "status": status.value
    }
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201
    assert response.json()["status"] == status.value 