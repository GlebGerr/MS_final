import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Путь к базе данных из переменной окружения или по умолчанию в ./data/url.db
database_path = os.getenv("DATABASE_URL", "sqlite:///./data/url.db")

# Создаем движок для подключения к базе данных SQLite
engine = create_engine(
    database_path,
    connect_args={"check_same_thread": False}  # Для SQLite на одном потоке
)

# Сессия для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()
