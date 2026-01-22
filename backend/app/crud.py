"""
Модуль crud.py содержит функции для операций с базой данных.
CRUD = Create, Read, Update, Delete

Каждая функция работает с сессией базы данных и выполняет
одну конкретную операцию.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

# --- CREATE операции ---

def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """
    Создает новую задачу в базе данных.
    
    Args:
        db: сессия базы данных
        task: данные для создания задачи (схема TaskCreate)
    
    Returns:
        models.Task: созданный объект задачи
    
    Пример:
        new_task = create_task(db, TaskCreate(title="Купить молоко"))
    """
    # Создаем экземпляр модели Task из данных схемы
    db_task = models.Task(
        title=task.title,
        description=task.description
        # is_completed по умолчанию False
        # created_at и updated_at установятся автоматически
    )
    
    # Добавляем задачу в сессию
    db.add(db_task)
    
    # Сохраняем изменения в базе данных
    db.commit()
    
    # Обновляем объект, чтобы получить сгенерированный ID
    db.refresh(db_task)
    
    return db_task

# --- READ операции ---

def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """
    Получает задачу по ID.
    
    Args:
        db: сессия базы данных
        task_id: ID искомой задачи
    
    Returns:
        Optional[models.Task]: задача или None, если не найдена
    """
    # Используем метод query для поиска задачи по ID
    # filter_by ищет по точному совпадению
    # first() возвращает первый результат или None
    return db.query(models.Task).filter_by(id=task_id).first()

def get_tasks(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    completed: Optional[bool] = None
) -> List[models.Task]:
    """
    Получает список задач с пагинацией и фильтрацией.
    
    Args:
        db: сессия базы данных
        skip: сколько задач пропустить (для пагинации)
        limit: максимальное количество задач
        completed: фильтр по статусу выполнения (None - все задачи)
    
    Returns:
        List[models.Task]: список задач
    """
    # Начинаем запрос
    query = db.query(models.Task)
    
    # Применяем фильтр, если передан
    if completed is not None:
        query = query.filter_by(is_completed=completed)
    
    # Применяем пагинацию
    # order_by сортирует по дате создания (новые сначала)
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    
    return tasks

def get_tasks_count(db: Session, completed: Optional[bool] = None) -> int:
    """
    Получает общее количество задач (с фильтрацией).
    
    Args:
        db: сессия базы данных
        completed: фильтр по статусу выполнения
    
    Returns:
        int: количество задач
    """
    query = db.query(models.Task)
    
    if completed is not None:
        query = query.filter_by(is_completed=completed)
    
    return query.count()

# --- UPDATE операции ---

def update_task(
    db: Session, 
    task_id: int, 
    task_update: schemas.TaskUpdate
) -> Optional[models.Task]:
    """
    Обновляет существующую задачу.
    
    Args:
        db: сессия базы данных
        task_id: ID задачи для обновления
        task_update: данные для обновления
    
    Returns:
        Optional[models.Task]: обновленная задача или None, если не найдена
    """
    # Получаем задачу из базы данных
    db_task = get_task(db, task_id)
    
    # Если задача не найдена, возвращаем None
    if not db_task:
        return None
    
    # Преобразуем данные обновления в словарь, исключая None значения
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Обновляем поля задачи
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    # Сохраняем изменения
    db.commit()
    
    # Обновляем объект
    db.refresh(db_task)
    
    return db_task

def mark_task_completed(db: Session, task_id: int) -> Optional[models.Task]:
    """
    Отмечает задачу как выполненную.
    Это специализированная версия update_task.
    
    Args:
        db: сессия базы данных
        task_id: ID задачи
    
    Returns:
        Optional[models.Task]: обновленная задача или None
    """
    db_task = get_task(db, task_id)
    
    if not db_task:
        return None
    
    # Устанавливаем статус "выполнено"
    db_task.is_completed = True
    
    db.commit()
    db.refresh(db_task)
    
    return db_task

# --- DELETE операции ---

def delete_task(db: Session, task_id: int) -> bool:
    """
    Удаляет задачу из базы данных.
    
    Args:
        db: сессия базы данных
        task_id: ID задачи для удаления
    
    Returns:
        bool: True если задача удалена, False если не найдена
    """
    db_task = get_task(db, task_id)
    
    if not db_task:
        return False
    
    # Удаляем задачу
    db.delete(db_task)
    
    # Сохраняем изменения
    db.commit()
    
    return True