from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app import crud
from app.database import engine, get_db, SessionLocal
from app import models
from pydantic import BaseModel
import requests
import random
import os
from mimesis import Text
from datetime import datetime
import sys
import pathlib

# Добавляем корневую директорию в путь
sys.path.append(str(pathlib.Path(__file__).parent.parent))

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Triple Generator: Цвет + Слово + Усложнение")

# Настраиваем пути к шаблонам и статическим файлам
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Модели для ответа
class ChallengeResponse(BaseModel):
    category: str
    name: str
    description: str


class ColorResponse(BaseModel):
    name: str
    hex: str


class WordResponse(BaseModel):
    word: str


def get_random_color():
    """Получаем случайный цвет с обработкой ошибок"""
    try:
        response = requests.get('https://www.thecolorapi.com/random', timeout=3)
        response.raise_for_status()

        data = response.json()
        return {
            'name': data['name']['value'],
            'hex': data['hex']['value']
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Сервис цветов временно недоступен: {str(e)}"
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=502,
            detail=f"Некорректный ответ от сервиса цветов: {str(e)}"
        )


def get_random_word():
    """Случайное русское слово"""
    text_gen = Text('ru')
    return text_gen.word()


"""Инициализация данных при запуске"""
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        crud.create_initial_data(db)
        print("Данные успешно загружены")
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request, db: Session = Depends(get_db)):
    """Главная страница с тремя генерациями"""
    # Получаем начальные данные
    color = get_random_color()
    word = get_random_word()
    challenge_result = crud.get_random_challenge(db)

    if challenge_result:
        challenge = {
            'category': challenge_result['category'].name,
            'name': challenge_result['challenge'].name,
            'description': challenge_result['challenge'].description
        }
    else:
        challenge = {
            'category': 'Усложнение',
            'name': 'Базовое задание',
            'description': 'Создайте рисунок на свободную тему'
        }

    return templates.TemplateResponse("index.html", {
        "request": request,
        "color": color,
        "word": word,
        "challenge": challenge
    })


# API эндпоинты
@app.get("/api/random-color", response_model=ColorResponse)
async def api_random_color():
    """API для получения случайного цвета"""
    color = get_random_color()
    return ColorResponse(**color)


@app.get("/api/random-word", response_model=WordResponse)
async def api_random_word():
    """API для получения случайного слова"""
    return WordResponse(word=get_random_word())


@app.get("/api/random-challenge", response_model=ChallengeResponse)
async def api_random_challenge(db: Session = Depends(get_db)):
    """API для получения случайного усложнения"""
    result = crud.get_random_challenge(db)

    if not result:
        raise HTTPException(status_code=404, detail="No challenges available")

    return ChallengeResponse(
        category=result["category"].name,
        name=result["challenge"].name,
        description=result["challenge"].description
    )


@app.get("/api/random-all")
async def api_random_all(db: Session = Depends(get_db)):
    """API для получения всех трех случайных значений"""
    color = get_random_color()
    word = get_random_word()

    result = crud.get_random_challenge(db)
    if result:
        challenge = {
            'category': result["category"].name,
            'name': result["challenge"].name,
            'description': result["challenge"].description
        }
    else:
        challenge = {
            'category': 'Усложнение',
            'name': 'Базовое задание',
            'description': 'Создайте рисунок на свободную тему'
        }

    return {
        'color': color,
        'word': word,
        'challenge': challenge
    }


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Triple Generator"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)