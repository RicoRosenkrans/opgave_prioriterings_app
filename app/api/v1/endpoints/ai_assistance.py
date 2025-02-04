from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict
from app.models.base import get_session
from app.models.task import Task
from app.ai.chains.task_prioritization import TaskPrioritizationChain
from app.ai.chains.status_report import StatusReportChain

router = APIRouter()
prioritization_chain = TaskPrioritizationChain()
status_report_chain = StatusReportChain()

@router.post("/prioritize/{task_id}", response_model=Dict[str, str])
async def get_task_priority_suggestion(
    task_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Få et forslag til prioritering af en specifik opgave"""
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    suggestion = await prioritization_chain.get_priority_suggestion(task)
    return suggestion

@router.post("/prioritize-batch", response_model=List[Dict[str, str]])
async def batch_prioritize_tasks(
    db: AsyncSession = Depends(get_session)
):
    """Få prioriteringsforslag for alle aktive opgaver"""
    query = select(Task).where(Task.status != "done")
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    suggestions = await prioritization_chain.batch_prioritize(tasks)
    return suggestions

@router.get("/status-report", response_model=str)
async def generate_status_report(
    db: AsyncSession = Depends(get_session)
):
    """Generer en daglig statusrapport baseret på alle opgaver"""
    query = select(Task)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    report = await status_report_chain.generate_status_report(tasks)
    return report 