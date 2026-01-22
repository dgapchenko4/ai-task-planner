"""
Модуль models.py определяет структуру базы данных.
Здесь мы создаем классы (модели), которые соответствуют таблицам в SQLite.
Каждый класс - это таблица, каждый атрибут - это колонка в таблице.
"""

# Импортируем необходимые компоненты из SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

# Создаем базовый класс для всех моделей
# Все наши модели будут наследоваться от этого класса
Base = declarative_base()

class Task(Base):
    """
    Модель Task представляет собой таблицу 'tasks' в базе данных.
    Эта таблица будет хранить все задачи пользователя.
    
    Атрибуты класса становятся колонками в таблице:
    - id: уникальный идентификатор задачи (первичный ключ)
    - title: заголовок задачи (обязательное поле)
    - description: подробное описание задачи (может быть пустым)
    - is_completed: статус выполнения (False по умолчанию)
    - created_at: дата и время создания (автоматически устанавливается)
    - updated_at: дата и время последнего обновления
    """
    
    # Указываем имя таблицы в базе данных
    __tablename__ = "tasks"
    
    # Колонка 'id' - первичный ключ, автоинкремент
    # Integer: тип данных - целое число
    # primary_key=True: это первичный ключ
    # autoincrement=True: автоматически увеличивается при добавлении новой записи
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Колонка 'title' - заголовок задачи
    # String(255): тип данных - строка с максимальной длиной 255 символов
    # nullable=False: поле не может быть пустым (NOT NULL в SQL)
    # index=True: создает индекс для ускорения поиска
    title = Column(String(255), nullable=False, index=True)
    
    # Колонка 'description' - описание задачи
    # Text: тип данных для длинного текста (без ограничения длины)
    # nullable=True: поле может быть пустым
    # default=None: значение по умолчанию - None (NULL в SQL)
    description = Column(Text, nullable=True, default=None)
    
    # Колонка 'is_completed' - статус выполнения задачи
    # Boolean: тип данных - логическое значение (True/False)
    # default=False: по умолчанию задача не выполнена
    # nullable=False: поле обязательно для заполнения
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Колонка 'created_at' - время создания задачи
    # DateTime: тип данных - дата и время
    # server_default=func.now(): значение по умолчанию - текущее время сервера
    # Это означает, что при создании записи автоматически ставится текущая дата/время
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Колонка 'updated_at' - время последнего обновления задачи
    # onupdate=func.now(): автоматически обновляется при изменении записи
    # default=func.now(): значение по умолчанию - текущее время
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        """
        Магический метод для строкового представления объекта.
        Вызывается при использовании print(task) или str(task).
        """
        return f"<Task(id={self.id}, title='{self.title}', completed={self.is_completed})>"