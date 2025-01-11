import uuid
import logging
from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import URLItem, URLStatistics

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s : %(message)s')

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройка CORS для работы с любыми источниками
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для создания URL
class URLCreate(BaseModel):
    url: HttpUrl

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Генерация уникального короткого идентификатора для URL
def generate_short_id(length=6):
    return uuid.uuid4().hex[:length]

@app.post("/shorten")
def shorten_url(
    item: URLCreate,
    request: Request,
    modifyer: str = Query(None, alias="modifier"),
    db: Session = Depends(get_db)
):
    # Проверка, существует ли уже URL в базе
    existing_url = db.query(URLItem).filter(URLItem.full_url == str(item.url)).first()
    if existing_url:
        # Если URL уже существует, возвращаем его короткую ссылку
        return {"short_url": f"{request.base_url}/{existing_url.short_id}"}

    # Попытка сгенерировать уникальный короткий ID
    for _ in range(10):
        short_id = generate_short_id()
        if modifyer:
            short_id = modifyer + short_id  # Добавление модификатора

        # Проверка, что короткая ссылка уникальна
        existing_short_url = db.query(URLItem).filter(URLItem.short_id == short_id).first()
        if not existing_short_url:
            # Если короткий ID уникален, создаем новый элемент
            new_item = URLItem(short_id=short_id, full_url=str(item.url))
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            return {"short_url": f"{request.base_url}/{short_id}"}

    # Если не удалось найти уникальный короткий ID, возвращаем ошибку
    raise HTTPException(status_code=500, detail="Не удалось сгенерировать короткую ссылку")

@app.get("/{short_id}")
def redirect_to_full(short_id: str, request: Request, db: Session = Depends(get_db)):
    # Получаем полный URL по короткому ID
    url_item = db.query(URLItem).filter(URLItem.short_id == short_id).first()
    if not url_item:
        # Если короткая ссылка не найдена, возвращаем ошибку
        raise HTTPException(status_code=404, detail="Короткая ссылка не найдена")

    # Логируем информацию о переходе по ссылке
    user_agent = request.headers.get('user-agent', 'Unknown')
    user_ip = request.client.host if request.client else 'Unknown'
    url_stats = URLStatistics(
        url_item_id=url_item.full_url,
        user_agent=user_agent,
        user_ip=user_ip
    )
    db.add(url_stats)
    db.commit()
    db.refresh(url_stats)

    # Логируем переход
    logging.debug(f"Переход по короткой ссылке на {url_item.full_url}")

    # Перенаправляем на полный URL
    return RedirectResponse(url=url_item.full_url, status_code=302)

@app.get("/stats/{short_id}")
def get_stats(short_id: str, db: Session = Depends(get_db)):
    # Получаем статистику по короткому ID
    url_item = db.query(URLItem).filter(URLItem.short_id == short_id).first()
    if not url_item:
        raise HTTPException(status_code=404, detail="Короткая ссылка не найдена")

    # Возвращаем статистику по переходам по ссылке
    stats = db.query(URLStatistics).filter(URLStatistics.url_item_id == url_item.full_url).all()
    return {
        "short_id": url_item.short_id,
        "full_url": url_item.full_url,
        "stats": stats
    }
