"""
Модуль schemas.py содержит Pydantic схемы для валидации данных.
Pydantic гарантирует, что данные, которые приходят в API или уходят из него,
соответствуют определенной структуре и типам.

Схемы используются для:
1. Валидации входных данных (например, при создании задачи)
2. Сериализации выходных данных (например, при возврате списка задач)
3. Документации API (FastAPI автоматически генерирует документацию из схем)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Базовые схемы для задач

class TaskBase(BaseModel):
    """
    Базовая схема для задачи.
    Содержит поля, общие для всех операций с задачами.
    """
    title: str = Field(
        ...,  # Многоточие означает, что поле обязательное
        min_length=1,
        max_length=255,
        description="Заголовок задачи (от 1 до 255 символов)"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Подробное описание задачи (максимум 2000 символов)"
    )

class TaskCreate(TaskBase):
    """
    Схема для создания новой задачи.
    Наследуется от TaskBase и может добавлять дополнительные поля или валидацию.
    """
    # В этом случае мы просто наследуем все поля из TaskBase
    # При создании задачи статус is_completed по умолчанию False
    
    @validator('title')
    def title_cannot_be_empty(cls, v):
        """
        Валидатор для поля title.
        Проверяет, что заголовок не состоит только из пробелов.
        
        Args:
            v: значение поля title
        
        Returns:
            str: проверенное значение
        
        Raises:
            ValueError: если заголовок состоит только из пробелов
        """
        if v.strip() == "":
            raise ValueError("Заголовок задачи не может быть пустым")
        return v.strip()

class TaskUpdate(BaseModel):
    """
    Схема для обновления существующей задачи.
    Все поля optional, так как при обновлении можно изменить только часть полей.
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Новый заголовок задачи"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Новое описание задачи"
    )
    is_completed: Optional[bool] = Field(
        None,
        description="Статус выполнения задачи"
    )
    
    class Config:
        """
        Конфигурация Pydantic модели.
        extra='forbid' запрещает передавать поля, не указанные в схеме.
        """
        extra = 'forbid'

class TaskInDBBase(TaskBase):
    """
    Базовая схема для задачи из базы данных.
    Содержит все поля, которые есть у задачи в БД.
    """
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """
        Конфигурация для работы с ORM.
        orm_mode=True позволяет Pydantic читать данные из SQLAlchemy объектов.
        """
        from_attributes = True  # В новых версиях Pydantic вместо orm_mode

class Task(TaskInDBBase):
    """
    Схема для возврата задачи клиенту.
    Наследует все поля из TaskInDBBase.
    """
    pass

class TaskList(BaseModel):
    """
    Схема для возврата списка задач.
    Содержит список задач и общее количество.
    """
    tasks: List[Task]
    total: int