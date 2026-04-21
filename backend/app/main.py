"""
Основной модуль FastAPI приложения для AI Task Planner.
Это исправленная версия с полной поддержкой CRUD операций.
"""

# Импорт стандартных библиотек Python
import datetime  # Для работы с датами и временем

# Импорт компонентов FastAPI
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware  # Для обработки CORS (кросс-доменных запросов)
from fastapi.responses import JSONResponse  # Для возврата JSON ответов
from pydantic import BaseModel  # Для валидации данных (Pydantic модели)
from sqlalchemy.orm import Session  # Для работы с сессиями базы данных
from typing import Optional, List  # Для аннотации типов (опциональные параметры, списки)

# Импорт собственных модулей проекта
from app.database import SessionLocal, engine, init_db  # Настройки базы данных
from app import models  # Модели SQLAlchemy (таблицы базы данных)

# Создание таблиц в базе данных при импорте модуля
models.Base.metadata.create_all(bind=engine)

# ============================================================================
# PYDANTIC МОДЕЛИ ДЛЯ ВАЛИДАЦИИ ДАННЫХ
# ============================================================================

class TaskCreate(BaseModel):
    """
    Модель для создания новой задачи.
    Используется для валидации входных данных при POST запросе.
    
    Attributes:
        title (str): Заголовок задачи (обязательное поле)
        description (Optional[str]): Описание задачи (может быть пустым)
        is_completed (bool): Статус выполнения (по умолчанию False)
    """
    title: str
    description: Optional[str] = None
    is_completed: bool = False

class TaskUpdate(BaseModel):
    """
    Модель для обновления существующей задачи.
    Все поля опциональны - можно обновлять только часть полей.
    
    Attributes:
        title (Optional[str]): Новый заголовок задачи
        description (Optional[str]): Новое описание задачи
        is_completed (Optional[bool]): Новый статус выполнения
    """
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    
    class Config:
        """Конфигурация Pydantic модели."""
        # Позволяет использовать модель с SQLAlchemy объектами
        from_attributes = True
        # Запрещает передачу дополнительных полей, не указанных в модели
        extra = "forbid"

# ============================================================================
# СОЗДАНИЕ И НАСТРОЙКА FASTAPI ПРИЛОЖЕНИЯ
# ============================================================================

app = FastAPI(
    title="AI Task Planner API",  # Название API
    description="API для планировщика задач с AI-ассистентом",  # Описание
    version="1.0.0"  # Версия API
)

# Настройка CORS (Cross-Origin Resource Sharing)
# Это необходимо для разрешения запросов с фронтенда (Vue.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых доменов (для разработки)
    allow_credentials=True,  # Разрешаем отправку cookies
    allow_methods=["*"],  # Разрешаем все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def get_db():
    """
    Функция-генератор для получения сессии базы данных.
    
    Эта функция используется как dependency в эндпоинтах FastAPI.
    Каждый запрос получает свою сессию базы данных, которая автоматически
    закрывается после завершения обработки запроса.
    
    Yields:
        Session: Сессия SQLAlchemy для работы с базой данных
    """
    # Создаем новую сессию базы данных
    db = SessionLocal()
    try:
        # Возвращаем сессию для использования в эндпоинте
        yield db
    finally:
        # Закрываем сессию после завершения работы (даже если произошла ошибка)
        db.close()

def task_to_dict(task: models.Task) -> dict:
    """
    Преобразует объект SQLAlchemy Task в словарь.
    
    Args:
        task (models.Task): Объект задачи из базы данных
        
    Returns:
        dict: Словарь с данными задачи в формате для JSON
    """
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }

# ============================================================================
# ЭНДПОИНТЫ API
# ============================================================================

@app.get("/")
def root():
    """
    Корневой эндпоинт для проверки работоспособности API.
    
    Returns:
        dict: Информация о API и доступных эндпоинтах
    """
    return {
        "message": "AI Task Planner API работает!",
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/tasks",
            "create_task": "/tasks (POST)",
            "get_task": "/tasks/{id}",
            "update_task": "/tasks/{id} (PUT)",
            "delete_task": "/tasks/{id} (DELETE)",
            "complete_task": "/tasks/{id}/complete (PATCH)"
        }
    }

@app.get("/tasks")
def get_tasks(
    skip: int = Query(0, ge=0, description="Количество пропущенных задач"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество задач"),
    completed: Optional[bool] = Query(None, description="Фильтр по статусу выполнения"),
    db: Session = Depends(get_db)
):
    """
    Получает список задач с поддержкой пагинации и фильтрации.
    
    Args:
        skip (int): Сколько задач пропустить (для пагинации)
        limit (int): Максимальное количество возвращаемых задач
        completed (Optional[bool]): Фильтр по статусу выполнения (True - выполненные, False - активные, None - все)
        db (Session): Сессия базы данных (автоматически инжектируется FastAPI)
    
    Returns:
        dict: Словарь с задачами и общим количеством
    """
    try:
        # Создаем базовый запрос к таблице задач
        query = db.query(models.Task)
        
        # Применяем фильтр по статусу выполнения, если он указан
        if completed is not None:
            query = query.filter(models.Task.is_completed == completed)
        
        # Получаем общее количество задач (для пагинации на фронтенде)
        total = query.count()
        
        # Применяем пагинацию и сортировку (новые задачи сначала)
        tasks = query.appointment_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
        
        # Преобразуем объекты SQLAlchemy в словари для JSON сериализации
        tasks_list = [task_to_dict(task) for task in tasks]
        
        # Логируем успешное выполнение (для отладки)
        print(f"✅ Получено {len(tasks_list)} задач (всего в БД: {total})")
        
        return {
            "tasks": tasks_list,
            "total": total
        }
        
    except Exception as e:
        # Логируем ошибку и возвращаем 500 статус
        print(f"❌ Ошибка при получении задач: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.post("/tasks")
def create_task(
    task: TaskCreate,  # Валидируем входные данные с помощью Pydantic модели
    db: Session = Depends(get_db)
):
    """
    Создает новую задачу.
    
    Args:
        task (TaskCreate): Данные для создания задачи (валидируются Pydantic)
        db (Session): Сессия базы данных
    
    Returns:
        dict: Созданная задача
    
    Raises:
        HTTPException: 400 если заголовок пустой, 500 при внутренней ошибке
    """
    try:
        # Проверяем, что заголовок не пустой
        if not task.title or not task.title.strip():
            raise HTTPException(status_code=400, detail="Заголовок задачи не может быть пустым")
        
        # Создаем новый объект задачи
        new_task = models.Task(
            title=task.title.strip(),
            description=task.description.strip() if task.description else None,
            is_completed=task.is_completed,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        
        # Добавляем задачу в сессию
        db.add(new_task)
        
        # Сохраняем изменения в базе данных
        db.commit()
        
        # Обновляем объект из базы данных (получаем сгенерированный ID)
        db.refresh(new_task)
        
        # Логируем успешное создание
        print(f"✅ Создана новая задача: ID={new_task.id}, title='{new_task.title}'")
        
        # Возвращаем созданную задачу
        return task_to_dict(new_task)
        
    except HTTPException:
        # Пробрасываем HTTPException дальше (например, ошибка 400)
        raise
    except Exception as e:
        # Откатываем транзакцию при ошибке
        db.rollback()
        print(f"❌ Ошибка при создании задачи: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Получает задачу по её ID.
    
    Args:
        task_id (int): ID искомой задачи
        db (Session): Сессия базы данных
    
    Returns:
        dict: Найденная задача
    
    Raises:
        HTTPException: 404 если задача не найдена
    """
    # Ищем задачу в базе данных по ID
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    # Если задача не найдена, возвращаем 404 ошибку
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Возвращаем найденную задачу
    return task_to_dict(task)

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_update: TaskUpdate,  # Валидируем данные обновления с помощью Pydantic
    db: Session = Depends(get_db)
):
    """
    Обновляет существующую задачу.
    Все поля опциональны - можно обновлять только часть полей.
    
    Args:
        task_id (int): ID задачи для обновления
        task_update (TaskUpdate): Данные для обновления
        db (Session): Сессия базы данных
    
    Returns:
        dict: Обновленная задача
    
    Raises:
        HTTPException: 404 если задача не найдена, 500 при внутренней ошибке
    """
    # Ищем задачу в базе данных
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    try:
        # Логируем полученные данные обновления
        print(f"🔄 Обновление задачи ID={task_id}")
        print(f"   Полученные данные: {task_update.dict(exclude_unset=True)}")
        
        # Преобразуем Pydantic модель в словарь, исключая поля со значениями по умолчанию
        update_data = task_update.dict(exclude_unset=True)
        
        # Флаг для отслеживания, были ли изменения
        has_changes = False
        
        # Обновляем заголовок, если он передан
        if 'title' in update_data and update_data['title'] is not None:
            new_title = update_data['title'].strip()
            if new_title != task.title:  # Проверяем, действительно ли изменилось значение
                task.title = new_title
                has_changes = True
                print(f"   Заголовок обновлен: '{new_title}'")
        
        # Обновляем описание, если оно передано
        if 'description' in update_data:
            # Важно: description может быть явно передано как None
            new_description = update_data['description']
            
            if new_description is None:
                # Если передано None, очищаем описание
                if task.description is not None:
                    task.description = None
                    has_changes = True
                    print(f"   Описание очищено")
            else:
                # Если передана строка, обрезаем пробелы
                new_description = new_description.strip()
                if new_description != (task.description or ""):
                    task.description = new_description or None
                    has_changes = True
                    print(f"   Описание обновлено: '{new_description}'")
        
        # Обновляем статус выполнения, если он передан
        if 'is_completed' in update_data and update_data['is_completed'] is not None:
            new_status = update_data['is_completed']
            if new_status != task.is_completed:
                task.is_completed = new_status
                has_changes = True
                print(f"   Статус выполнения обновлен: {new_status}")
        
        # Если были изменения, обновляем updated_at и сохраняем в БД
        if has_changes:
            task.updated_at = datetime.datetime.now()
            db.commit()  # Сохраняем изменения в базе данных
            db.refresh(task)  # Обновляем объект из БД
            print(f"✅ Задача ID={task_id} успешно обновлена")
        else:
            print(f"ℹ️  Задача ID={task_id} не изменилась (данные идентичны)")
        
        # Возвращаем обновленную (или неизмененную) задачу
        return task_to_dict(task)
        
    except Exception as e:
        # Откатываем транзакцию при ошибке
        db.rollback()
        print(f"❌ Ошибка при обновлении задачи ID={task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Удаляет задачу по её ID.
    
    Args:
        task_id (int): ID задачи для удаления
        db (Session): Сессия базы данных
    
    Returns:
        dict: Сообщение об успешном удалении
    
    Raises:
        HTTPException: 404 если задача не найдена, 500 при внутренней ошибке
    """
    # Ищем задачу в базе данных
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    try:
        # Логируем удаление
        print(f"🗑️  Удаление задачи ID={task_id}, title='{task.title}'")
        
        # Удаляем задачу
        db.delete(task)
        
        # Сохраняем изменения в базе данных
        db.commit()
        
        print(f"✅ Задача ID={task_id} успешно удалена")
        
        # Возвращаем сообщение об успехе (статус 200 по умолчанию)
        return {"message": "Задача успешно удалена"}
        
    except Exception as e:
        # Откатываем транзакцию при ошибке
        db.rollback()
        print(f"❌ Ошибка при удалении задачи ID={task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Отмечает задачу как выполненную.
    Это специализированный эндпоинт для быстрого завершения задач.
    
    Args:
        task_id (int): ID задачи для отметки как выполненной
        db (Session): Сессия базы данных
    
    Returns:
        dict: Обновленная задача
    
    Raises:
        HTTPException: 404 если задача не найдена, 500 при внутренней ошибке
    """
    # Ищем задачу в базе данных
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    try:
        # Проверяем, не выполнена ли задача уже
        if task.is_completed:
            print(f"ℹ️  Задача ID={task_id} уже была выполнена")
        else:
            # Отмечаем задачу как выполненную
            task.is_completed = True
            task.updated_at = datetime.datetime.now()
            
            # Сохраняем изменения
            db.commit()
            db.refresh(task)
            
            print(f"✅ Задача ID={task_id} отмечена как выполненная")
        
        # Возвращаем обновленную задачу
        return task_to_dict(task)
        
    except Exception as e:
        # Откатываем транзакцию при ошибке
        db.rollback()
        print(f"❌ Ошибка при выполнении задачи ID={task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/favicon.ico")
def favicon():
    """
    Простой эндпоинт для favicon.ico чтобы избежать ошибок 404 в логах.
    
    Returns:
        JSONResponse: Простое сообщение
    """
    return JSONResponse(content={"message": "No favicon"})

# ============================================================================
# ЗАПУСК СЕРВЕРА
# ============================================================================

if __name__ == "__main__":
    """
    Точка входа для запуска приложения напрямую (python main.py).
    В bookion обычно используется uvicorn напрямую.
    """
    import uvicorn
    
    # Запускаем сервер Uvicorn
    uvicorn.run(
        "app.main:app",  # Импортируемый объект приложения
        host="0.0.0.0",  # Слушаем все сетевые интерфейсы
        port=8000,  # Порт для прослушивания
        reload=True,  # Автоматическая перезагрузка при изменении кода (только для разработки!)
        log_level="info"  # Уровень логирования
    )