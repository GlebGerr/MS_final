# Используем официальный образ Python 3.13.1
FROM python:3.13.1-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей и устанавливаем необходимые библиотеки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения в контейнер
COPY . .

# Объявляем том для хранения базы данных
VOLUME ["/shorturl_app/data"]

# Устанавливаем переменную окружения для Python, чтобы отключить буферизацию вывода
ENV PYTHONUNBUFFERED=1

# Запускаем приложение с помощью Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
