from datetime import datetime
from typing import List, Union
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import TodoItem as TodoItemModel
from models import ItemNotification as ItemNotificationModel

# Создание всех таблиц в базе данных при старте приложения
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Модель для создания задачи
class TodoCreate(BaseModel):
    title: str
    description: Union[str, None] = None
    completed: bool = False

# Модель для представления задачи
class TodoItem(TodoCreate):
    class Config:
        orm_mode = True

# Модель для создания уведомления
class ItemNotificationCreate(BaseModel):
    notion_description: Union[str, None] = None
    expiration_time: datetime = datetime.now()
    autocomplete: bool = False

# Модель для представления уведомления
class ItemNotification(ItemNotificationCreate):
    todo_item_id: int

    class Config:
        orm_mode = True

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Получение всех уведомлений для конкретной задачи
@app.get("/items/{item_id}/notifications", response_model=Union[List[ItemNotification], ItemNotification])
def get_notifications(item_id: int, db: Session = Depends(get_db)):
    notifications = db.query(ItemNotificationModel).filter(ItemNotificationModel.todo_item_id == item_id).all()
    if notifications:
        return notifications
    raise HTTPException(status_code=404, detail="Item not found")

# Получение конкретного уведомления по ID
@app.get("/items/{item_id}/notifications/{notification_id}", response_model=ItemNotification)
def get_notification(item_id: int, notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(ItemNotificationModel).filter(ItemNotificationModel.todo_item_id == item_id, 
                                                          ItemNotificationModel.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

# Создание нового уведомления для задачи
@app.post("/items/{item_id}/notifications", response_model=ItemNotification)
def create_notification(item_id: int, notification_data: ItemNotificationCreate, db: Session = Depends(get_db)):
    todo_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if not todo_item:
        raise HTTPException(status_code=404, detail="Item not found")

    new_notification = ItemNotificationModel(
        todo_item_id=item_id,
        notion_description=notification_data.notion_description,
        expiration_time=notification_data.expiration_time,
        autocomplete=notification_data.autocomplete
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

# Удаление всех уведомлений для задачи
@app.delete("/items/{item_id}/notifications")
def delete_notifications(item_id: int, db: Session = Depends(get_db)):
    todo_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if not todo_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.query(ItemNotificationModel).filter(ItemNotificationModel.todo_item_id == item_id).delete()
    db.commit()
    return {"message": "Notifications deleted successfully"}

# Удаление конкретного уведомления по ID
@app.delete("/items/{item_id}/notifications/{notification_id}")
def delete_notification(item_id: int, notification_id: int, db: Session = Depends(get_db)):
    todo_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if not todo_item:
        raise HTTPException(status_code=404, detail="Item not found")

    notification = db.query(ItemNotificationModel).filter(ItemNotificationModel.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}

# Получение всех задач
@app.get("/items", response_model=List[TodoItem])
def get_items(db: Session = Depends(get_db)):
    return db.query(TodoItemModel).all()

# Получение конкретной задачи по ID
@app.get("/items/{item_id}", response_model=TodoItem)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Создание новой задачи
@app.post("/items", response_model=TodoItem)
def create_item(item: TodoCreate, db: Session = Depends(get_db)):
    new_item = TodoItemModel(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# Обновление задачи по ID
@app.put("/items/{item_id}", response_model=TodoItem)
def update_item(item_id: int, item: TodoCreate, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.dict().items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item

# Удаление задачи по ID
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemModel).filter(TodoItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}