from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
import random
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


def get_data_file_path():
    """Получить путь к файлу данных из переменной окружения"""
    data_file = os.getenv("DATA_FILE")

    if not data_file:
        raise ValueError("Переменная окружения DATA_FILE не установлена")

    # Проверяем существование файла
    if not os.path.exists(data_file):
        # Пытаемся найти в текущей директории
        if os.path.exists("data.txt"):
            return "data.txt"
        raise FileNotFoundError(f"Файл данных не найден: {data_file}")

    return data_file


def get_random_challenge(db: Session):
    """Получить случайное усложнение"""
    random_challenge = db.query(models.Challenge).order_by(func.random()).first()

    if not random_challenge:
        raise HTTPException(status_code=404, detail="Нет доступных усложнений")

    category = random_challenge.category
    return {
        "category": category,
        "challenge": random_challenge
    }


def load_data_from_file(file_path: str = None):
    """Загрузить данные из текстового файла"""
    # Если путь не указан, используем переменную окружения
    if file_path is None:
        file_path = get_data_file_path()

    categories_data = []
    current_category = None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()

                if line.startswith('Категория:'):
                    category_name = line.replace('Категория:', '').strip()
                    current_category = {
                        'name': category_name,
                        'challenges': []
                    }
                    categories_data.append(current_category)

                elif line.startswith('-') and current_category:
                    challenge_line = line[1:].strip()

                    if ':' in challenge_line:
                        name, description = challenge_line.split(':', 1)
                        current_category['challenges'].append({
                            'name': name.strip(),
                            'description': description.strip()
                        })

    except FileNotFoundError as e:
        print(f"Файл {file_path} не найден: {e}")
        raise
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        raise

    return categories_data


def create_initial_data(db: Session, data_file: str = None):
    """Создать начальные данные из файла, если таблицы пусты"""
    if db.query(models.ChallengeCategory).count() == 0:
        print("Загрузка данных из файла...")

        try:
            # Если файл не указан, используем переменную окружения
            if data_file is None:
                data_file = get_data_file_path()

            categories_data = load_data_from_file(data_file)

            for category_data in categories_data:
                category = models.ChallengeCategory(name=category_data['name'])
                db.add(category)
                db.flush()

                for challenge_data in category_data['challenges']:
                    challenge = models.Challenge(
                        name=challenge_data['name'],
                        description=challenge_data['description'],
                        category_id=category.id
                    )
                    db.add(challenge)

            db.commit()
            print(f"Загружено {len(categories_data)} категорий с усложнениями из файла {data_file}")

        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
            print("Продолжаем без загрузки данных...")
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            db.rollback()
            raise
    else:
        print("Данные уже существуют в базе.")