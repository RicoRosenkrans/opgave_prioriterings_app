import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app.models.task import TaskPriority, TaskStatus

# Mock responses
MOCK_PRIORITY_RESPONSE = """
Anbefalet prioritet: HIGH
Begrundelse: Opgaven har en tæt deadline og høj kompleksitet
"""

MOCK_STATUS_REPORT = """
1. Overordnet status:
   Projektet skrider frem som planlagt

2. Fremskridt i dag:
   - Task 1 er færdiggjort
   - Task 2 er i gang

3. Blokeringer/Udfordringer:
   Ingen væsentlige blokeringer

4. Næste skridt:
   Fortsæt med planlagte opgaver
"""

@pytest.fixture
def mock_llm_chain():
    with patch('app.ai.chains.task_prioritization.ChatOpenAI'), \
         patch('app.ai.chains.status_report.ChatOpenAI'):
        yield

@pytest.fixture
def mock_prioritization_chain():
    with patch('app.ai.chains.task_prioritization.TaskPrioritizationChain') as mock:
        chain_instance = mock.return_value
        chain_instance.get_priority_suggestion = AsyncMock(return_value={
            "suggested_priority": "HIGH",
            "reasoning": "Opgaven har en tæt deadline og høj kompleksitet"
        })
        chain_instance.batch_prioritize = AsyncMock(return_value=[
            {
                "task_id": 1,
                "suggested_priority": "HIGH",
                "reasoning": "Tæt deadline"
            },
            {
                "task_id": 2,
                "suggested_priority": "MEDIUM",
                "reasoning": "Normal prioritet"
            }
        ])
        yield mock

@pytest.fixture
def mock_status_report_chain():
    with patch('app.ai.chains.status_report.StatusReportChain') as mock:
        chain_instance = mock.return_value
        chain_instance.generate_status_report = AsyncMock(return_value=MOCK_STATUS_REPORT)
        yield mock

async def test_get_task_priority_suggestion(
    client: TestClient,
    mock_llm_chain,
    mock_prioritization_chain
):
    # Opret en test task først
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": TaskPriority.MEDIUM.value,
        "status": TaskStatus.TODO.value,
        "deadline": datetime.now(timezone.utc).isoformat()
    }
    
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]
    
    # Test prioriteringsforslag
    response = client.post(f"/api/v1/ai/prioritize/{task_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "suggested_priority" in data
    assert "reasoning" in data
    assert data["suggested_priority"] == "HIGH"

async def test_get_task_priority_suggestion_not_found(
    client: TestClient,
    mock_llm_chain,
    mock_prioritization_chain
):
    response = client.post("/api/v1/ai/prioritize/999999")
    assert response.status_code == 404

async def test_batch_prioritize_tasks(
    client: TestClient,
    mock_llm_chain,
    mock_prioritization_chain
):
    # Opret nogle test tasks
    task_data = [
        {
            "title": "Task 1",
            "description": "Description 1",
            "status": TaskStatus.TODO.value
        },
        {
            "title": "Task 2",
            "description": "Description 2",
            "status": TaskStatus.IN_PROGRESS.value
        }
    ]
    
    for task in task_data:
        client.post("/api/v1/tasks/", json=task)
    
    # Test batch prioritering
    response = client.post("/api/v1/ai/prioritize-batch")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all("task_id" in item for item in data)
    assert all("suggested_priority" in item for item in data)
    assert all("reasoning" in item for item in data)

async def test_generate_status_report(
    client: TestClient,
    mock_llm_chain,
    mock_status_report_chain
):
    # Opret nogle test tasks
    task_data = [
        {
            "title": "Task 1",
            "description": "Description 1",
            "status": TaskStatus.DONE.value
        },
        {
            "title": "Task 2",
            "description": "Description 2",
            "status": TaskStatus.IN_PROGRESS.value
        }
    ]
    
    for task in task_data:
        client.post("/api/v1/tasks/", json=task)
    
    # Test status rapport generering
    response = client.get("/api/v1/ai/status-report")
    assert response.status_code == 200
    
    report = response.text
    assert "Overordnet status" in report
    assert "Fremskridt i dag" in report
    assert "Blokeringer/Udfordringer" in report
    assert "Næste skridt" in report

@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/ai/prioritize/1", "POST"),
    ("/api/v1/ai/prioritize-batch", "POST"),
    ("/api/v1/ai/status-report", "GET")
])
async def test_ai_endpoints_error_handling(
    client: TestClient,
    mock_llm_chain,
    endpoint: str,
    method: str
):
    # Test med ugyldig OpenAI API key
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'invalid_key'}):
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        
        # Vi forventer ikke 500 fejl selvom API key er ugyldig
        assert response.status_code != 500 