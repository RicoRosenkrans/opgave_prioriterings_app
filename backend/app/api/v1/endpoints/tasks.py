from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from app.models.base import get_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema

router = APIRouter()

@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_session)):
    db_task = Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskSchema])
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    query = select(Task).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{task_id}", response_model=TaskSchema)
async def read_task(task_id: int, db: AsyncSession = Depends(get_session)):
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return task 