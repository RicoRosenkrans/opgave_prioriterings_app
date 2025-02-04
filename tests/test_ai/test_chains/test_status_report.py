import pytest
from unittest.mock import patch, AsyncMock
from app.ai.chains.status_report import StatusReportChain
from app.models.task import Task, TaskStatus, TaskPriority
from datetime import datetime, timezone

@pytest.fixture
def mock_tasks():
    return [
        Task(
            id=1,
            title="Task 1",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH
        ),
        Task(
            id=2,
            title="Task 2",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM
        )
    ]

@pytest.mark.asyncio
async def test_status_report_success(mock_tasks):
    with patch('app.ai.chains.status_report.LLMChain') as mock_chain:
        chain_instance = mock_chain.return_value
        chain_instance.arun = AsyncMock(return_value="Test Report Content")
        
        reporter = StatusReportChain()
        report = await reporter.generate_status_report(mock_tasks)
        
        assert report == "Test Report Content"

@pytest.mark.asyncio
async def test_status_report_fallback(mock_tasks):
    with patch('app.ai.chains.status_report.LLMChain') as mock_chain:
        chain_instance = mock_chain.return_value
        chain_instance.arun = AsyncMock(side_effect=Exception("API Error"))
        
        reporter = StatusReportChain()
        report = await reporter.generate_status_report(mock_tasks)
        
        assert "Fallback Version" in report
        assert "Aktive opgaver: 1" in report  # 1 task in progress
        assert "Afsluttede opgaver: 1" in report  # 1 task done 