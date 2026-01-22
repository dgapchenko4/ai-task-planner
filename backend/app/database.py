"""
Упрощенный модуль для работы с базой данных.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL для подключения к SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# Создаем движок
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()

def init_db():
    """Инициализирует базу данных"""
    from app import models
    models.Base.metadata.create_all(bind=engine)
    print("База данных инициализирована")