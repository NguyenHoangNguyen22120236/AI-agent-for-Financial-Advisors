from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskRead
from app.models.task import Task
from app.db.session import get_db

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@tasks_router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return Task.create(db, user_id=1, type=task.type, task_metadata=task.task_metadata)


@tasks_router.get("/", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return Task.get_all_for_user(db, user_id=1)


@tasks_router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = Task.get_by_id(db, task_id=task_id, user_id=1)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@tasks_router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = Task.get_by_id(db, task_id=task_id, user_id=1)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.delete(db)
    return {"detail": "Deleted"}
