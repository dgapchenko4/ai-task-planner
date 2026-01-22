"""
Основной модуль FastAPI приложения.
Упрощенная версия для решения проблемы 422 ошибки.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import datetime
from pydantic import BaseModel
from typing import Optional

# Импортируем наши модули
from app.database import SessionLocal, engine, init_db
from app import models

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False

# Создаем таблицы при импорте
models.Base.metadata.create_all(bind=engine)

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="AI Task Planner API",
    description="API для планировщика задач с AI-ассистентом",
    version="1.0.0"
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Эндпоинты API ---

@app.get("/")
def root():
    """Проверка работы API"""
    return {
        "message": "AI Task Planner API работает!",
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/tasks",
            "create_task": "/tasks (POST)",
            "get_task": "/tasks/{id}",
            "update_task": "/tasks/{id} (PUT)",
            "delete_task": "/tasks/{id} (DELETE)"
        }
    }

@app.get("/tasks")
def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Получает список задач с пагинацией и фильтрацией.
    Упрощенная версия без Pydantic схем.
    """
    try:
        # Строим запрос
        query = db.query(models.Task)
        
        # Применяем фильтр по статусу, если указан
        if completed is not None:
            query = query.filter(models.Task.is_completed == completed)
        
        # Получаем общее количество
        total = query.count()
        
        # Получаем задачи с пагинацией
        tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
        
        # Преобразуем задачи в словари
        tasks_list = []
        for task in tasks:
            tasks_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            })
        
        return {
            "tasks": tasks_list,
            "total": total
        }
        
    except Exception as e:
        print(f"Ошибка в /tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Обновите эндпоинт create_task
@app.post("/tasks")
def create_task(
    task_data: TaskCreateRequest,  # Принимаем JSON
    db: Session = Depends(get_db)
):
    """Создает новую задачу (принимает JSON)"""
    try:
        # Проверяем заголовок
        if not task_data.title or not task_data.title.strip():
            raise HTTPException(status_code=400, detail="Заголовок не может быть пустым")
        
        # Создаем новую задачу
        new_task = models.Task(
            title=task_data.title.strip(),
            description=task_data.description.strip() if task_data.description else None,
            is_completed=task_data.is_completed,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        # Возвращаем созданную задачу
        return {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_completed": new_task.is_completed,
            "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
            "updated_at": new_task.updated_at.isoformat() if new_task.updated_at else None
        }
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при создании задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Получает задачу по ID"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Обновляет задачу"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    try:
        # Обновляем поля, если они переданы
        if title is not None:
            task.title = title.strip()
        
        if description is not None:
            task.description = description.strip() if description.strip() else None
        
        if is_completed is not None:
            task.is_completed = is_completed
        
        task.updated_at = datetime.datetime.now()
        
        db.commit()
        db.refresh(task)
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удаляет задачу"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    try:
        db.delete(task)
        db.commit()
        
        return {"message": "Задача успешно удалена"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Отмечает задачу как выполненную"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    try:
        task.is_completed = True
        task.updated_at = datetime.datetime.now()
        
        db.commit()
        db.refresh(task)
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинт для favicon.ico чтобы избежать ошибок
@app.get("/favicon.ico")
def favicon():
    return {"message": "No favicon"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)