# Используем официальный образ Python 3.13.1 (или ближайшую стабильную версию, если такой нет)
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . ./

# Объявляем том для хранения данных (для базы данных или других файлов)
VOLUME ["/app/data"]

# Устанавливаем переменную окружения, чтобы Python не буферизовал вывод
ENV PYTHONUNBUFFERED=1

# Запуск приложения с использованием Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
