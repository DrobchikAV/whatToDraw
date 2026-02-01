import pytest
import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import Base, get_db
from app.models import Challenge, ChallengeCategory

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost/test_db")


@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_engine():
    """Создаем движок для тестовой БД"""
    engine = create_engine(TEST_DATABASE_URL)

    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    yield engine

    # Очищаем после тестов
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Создаем сессию для тестов"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """Создаем тестовый клиент FastAPI"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def clean_db(db_session):
    """Очищает базу данных перед каждым тестом"""
    db_session.query(Challenge).delete()
    db_session.query(ChallengeCategory).delete()
    db_session.commit()
    yield
    db_session.rollback()


@pytest.fixture
def mock_requests():
    """Мок для requests"""
    with patch('app.main.requests') as mock:
        yield mock


@pytest.fixture
def sample_color_data():
    return {
        'name': {'value': 'Test Blue'},
        'hex': {'value': '#0000FF'}
    }


@pytest.fixture
def sample_challenge_data(db_session, clean_db):
    """Создает тестовые данные в БД"""
    category = ChallengeCategory(name="Test Category")
    db_session.add(category)
    db_session.flush()

    challenge = Challenge(
        name="Test Challenge",
        description="Test Description",
        category_id=category.id
    )
    db_session.add(challenge)
    db_session.commit()

    return {
        'category': category,
        'challenge': challenge
    }