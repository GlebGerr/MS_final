from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL подключения к базе данных (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/todo.db"

# Создание движка для подключения к базе данных
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Параметр для многозадачности в SQLite
)

# Создание сессии для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()

def init_db():
    """Инициализация базы данных (создание всех таблиц)"""
    Base.metadata.create_all(bind=engine)