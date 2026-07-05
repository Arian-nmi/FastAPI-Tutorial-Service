from fastapi import APIRouter, Path, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from tasks.schemas import *
from tasks.models import TaskModel
from sqlalchemy.orm import Session
from core.database import get_db
from auth.jwt_auth import get_authenticate_user
from users.models import UserModel
from typing import List


router = APIRouter(tags=["tasks"])

@router.get("/tasks", response_model=List[TaskResponseSchema])
async def retrieve_tasks_list(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticate_user),
    limit: int = Query(10, gt=0, le=50, description="Limiting the number of items to retrieve"),
    offset: int = Query(0, ge=0, description="Use for paginatingbased on passed items"),
    completed: bool = Query(None, description="Filter tasks based on beings completed or not")
    ):

    query = db.query(TaskModel).filter_by(userID=user.id)
    
    if completed is not None:
        query = query.filter_by(is_completed=completed)

    return query.limit(limit).offset(offset).all()


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_tasks_datail(task_id: int = Path(..., gt=0), user: UserModel = Depends(get_authenticate_user), db: Session = Depends(get_db)):
    task_obj = db.query(TaskModel).filter_by(userID=user.id, id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_obj


@router.post("/tasks", response_model=TaskResponseSchema)
async def create_tasks(request: TaskCreateSchema, db: Session = Depends(get_db), user: UserModel = Depends(get_authenticate_user)):
    data = request.model_dump()
    data.update({"userID": user.id})
    task_obj = TaskModel(**data)
    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)
    return task_obj


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(request: TaskUpdateSchema, user: UserModel = Depends(get_authenticate_user), task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_obj = db.query(TaskModel).filter_by(userID=user.id, id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(task_obj, field, value)

    db.commit()
    db.refresh(task_obj)

    return task_obj


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int = Path(..., gt=0), user: UserModel = Depends(get_authenticate_user), db: Session = Depends(get_db)):
    task_obj = db.query(TaskModel).filter_by(userID=user.id, id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task_obj)
    db.commit()

    return JSONResponse(content={"detail": "Task deleted successfully"}, status_code=200)