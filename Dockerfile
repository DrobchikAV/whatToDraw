FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY app/ app/
COPY tests/ tests/
COPY static/ static/
COPY templates/ templates/
COPY data.txt .
COPY .env.example .env

# Создание переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DATA_FILE=/app/data.txt

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]