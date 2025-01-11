from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from database import Base

# Модель для задачи
class TodoItem(Base):
    __tablename__ = "todo_items"

    # Основные поля задачи
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<TodoItem(id={self.id}, title={self.title}, completed={self.completed})>"

# Модель для уведомлений о задачах
class ItemNotification(Base):
    __tablename__ = "item_notifications"  # Исправлено название таблицы на "item_notifications" для согласованности

    # Основные поля уведомления
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todo_item_id = Column(Integer, ForeignKey("todo_items.id"), index=True)
    notion_description = Column(String, nullable=True)
    expiration_time = Column(DateTime)
    autocomplete = Column(Boolean, default=False)

    def __repr__(self):
        return f"<ItemNotification(id={self.id}, todo_item_id={self.todo_item_id}, expiration_time={self.expiration_time})>"
