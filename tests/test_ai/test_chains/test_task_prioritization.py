import pytest
from unittest.mock import patch, AsyncMock
from app.ai.chains.task_prioritization import TaskPrioritizationChain
from app.models.task import Task, TaskStatus, TaskPriority
from datetime import datetime, timezone

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

@pytest.mark.asyncio
async def test_priority_suggestion_success(mock_task):
    with patch('app.ai.chains.task_prioritization.LLMChain') as mock_chain:
        chain_instance = mock_chain.return_value
        chain_instance.arun = AsyncMock(return_value="""
        Anbefalet prioritet: HIGH
        Begrundelse: Test begrundelse
        """)
        
        prioritizer = TaskPrioritizationChain()
        result = await prioritizer.get_priority_suggestion(mock_task)
        
        assert result["suggested_priority"] == "HIGH"
        assert result["reasoning"] == "Test begrundelse"

@pytest.mark.asyncio
async def test_priority_suggestion_fallback(mock_task):
    with patch('app.ai.chains.task_prioritization.LLMChain') as mock_chain:
        chain_instance = mock_chain.return_value
        chain_instance.arun = AsyncMock(side_effect=Exception("API Error"))
        
        prioritizer = TaskPrioritizationChain()
        result = await prioritizer.get_priority_suggestion(mock_task)
        
        assert result["suggested_priority"] == "MEDIUM"  # Fallback værdi
        assert "Fejl" in result["reasoning"]
        assert "API Error" in result["reasoning"]

@pytest.mark.asyncio
async def test_batch_prioritize_partial_failure(mock_task):
    with patch('app.ai.chains.task_prioritization.LLMChain') as mock_chain:
        chain_instance = mock_chain.return_value
        # Første kald lykkes, andet fejler
        chain_instance.arun = AsyncMock(side_effect=[
            "Anbefalet prioritet: HIGH\nBegrundelse: Success",
            Exception("API Error")
        ])
        
        prioritizer = TaskPrioritizationChain()
        results = await prioritizer.batch_prioritize([mock_task, mock_task])
        
        assert len(results) == 2
        # Tjek første resultat (success)
        assert results[0]["task_id"] == mock_task.id
        assert results[0]["suggested_priority"] == "HIGH"
        assert results[0]["reasoning"] == "Success"
        
        # Tjek andet resultat (fallback)
        assert results[1]["task_id"] == mock_task.id
        assert results[1]["suggested_priority"] == "MEDIUM"
        assert "Fejl" in results[1]["reasoning"] 