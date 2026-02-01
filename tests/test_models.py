import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Challenge, ChallengeCategory


def test_create_challenge_category(db_session, clean_db):
    """Тест создания категории"""
    category = ChallengeCategory(name="Новая категория")
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert category.name == "Новая категория"
    assert len(category.challenges) == 0


def test_create_challenge(db_session, clean_db):
    """Тест создания усложнения"""
    category = ChallengeCategory(name="Тестовая категория")
    db_session.add(category)
    db_session.flush()

    challenge = Challenge(
        name="Тестовое задание",
        description="Описание тестового задания",
        category_id=category.id
    )

    db_session.add(challenge)
    db_session.commit()

    assert challenge.id is not None
    assert challenge.name == "Тестовое задание"
    assert challenge.description == "Описание тестового задания"
    assert challenge.category_id == category.id
    assert challenge.category == category


def test_challenge_category_relationship(db_session, clean_db):
    """Тест отношения между категорией и заданиями"""
    category = ChallengeCategory(name="Категория")

    challenge1 = Challenge(name="Задание 1", description="Описание 1")
    challenge2 = Challenge(name="Задание 2", description="Описание 2")

    category.challenges.extend([challenge1, challenge2])

    db_session.add(category)
    db_session.commit()

    # Проверяем обратную связь
    assert len(category.challenges) == 2
    assert challenge1.category == category
    assert challenge2.category == category
    assert challenge1 in category.challenges
    assert challenge2 in category.challenges


def test_challenge_without_category(db_session, clean_db):
    """Тест создания задания без категории (должно вызвать ошибку)"""
    challenge = Challenge(
        name="Задание без категории",
        description="Описание"
    )

    db_session.add(challenge)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()