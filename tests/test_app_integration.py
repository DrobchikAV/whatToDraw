import pytest
import os
from unittest.mock import patch, Mock
from fastapi import status
from sqlalchemy import text


@pytest.mark.integration
def test_user_complete_flow(client, db_session, clean_db):
    """
    Тест полного пользовательского сценария:
    1. Пользователь заходит на главную страницу
    2. Получает цвет, слово и усложнение
    3. Обновляет отдельные элементы
    4. Генерирует новую полную комбинацию
    """
    # 1. Загружаем тестовые данные в БД
    from app.models import ChallengeCategory, Challenge

    category1 = ChallengeCategory(name="Временное ограничение")
    category2 = ChallengeCategory(name="Художественный стиль")
    db_session.add_all([category1, category2])
    db_session.flush()

    challenges = [
        Challenge(name="30 секунд", description="0:30", category_id=category1.id),
        Challenge(name="Реализм", description="Изображение действительности", category_id=category2.id),
        Challenge(name="5 минут", description="5", category_id=category1.id)
    ]
    db_session.add_all(challenges)
    db_session.commit()

    # 2. Мокаем внешние API
    with patch('app.main.requests.get') as mock_requests, \
            patch('app.main.get_random_word') as mock_word:
        # Настройка моков для цветового API
        mock_color_response = Mock()
        mock_color_response.status_code = 200
        mock_color_response.json.return_value = {
            'name': {'value': 'Azure Blue'},
            'hex': {'value': '#007FFF'}
        }
        mock_requests.return_value = mock_color_response

        # Настройка мока для случайного слова
        mock_word.return_value = "вдохновение"

        # 3. Пользователь заходит на главную страницу
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "Azure Blue" in response.text
        assert "вдохновение" in response.text

        # 4. Пользователь получает новый цвет через API
        mock_color_response2 = Mock()
        mock_color_response2.status_code = 200
        mock_color_response2.json.return_value = {
            'name': {'value': 'Crimson Red'},
            'hex': {'value': '#DC143C'}
        }
        mock_requests.return_value = mock_color_response2

        color_response = client.get("/api/random-color")
        assert color_response.status_code == status.HTTP_200_OK
        color_data = color_response.json()
        assert color_data["name"] == "Crimson Red"
        assert color_data["hex"] == "#DC143C"

        # 5. Пользователь получает новое слово через API
        mock_word.return_value = "гармония"
        word_response = client.get("/api/random-word")
        assert word_response.status_code == status.HTTP_200_OK
        word_data = word_response.json()
        assert word_data["word"] == "гармония"

        # 6. Пользователь получает новое усложнение через API
        challenge_response = client.get("/api/random-challenge")
        assert challenge_response.status_code == status.HTTP_200_OK
        challenge_data = challenge_response.json()
        assert "category" in challenge_data
        assert "name" in challenge_data
        assert "description" in challenge_data
        assert challenge_data["name"] in ["30 секунд", "Реализм", "5 минут"]

        # 7. Пользователь генерирует новую полную комбинацию
        mock_color_response3 = Mock()
        mock_color_response3.status_code = 200
        mock_color_response3.json.return_value = {
            'name': {'value': 'Forest Green'},
            'hex': {'value': '#228B22'}
        }
        mock_requests.return_value = mock_color_response3
        mock_word.return_value = "природа"

        all_response = client.get("/api/random-all")
        assert all_response.status_code == status.HTTP_200_OK
        all_data = all_response.json()

        assert "color" in all_data
        assert "word" in all_data
        assert "challenge" in all_data
        assert all_data["color"]["name"] == "Forest Green"
        assert all_data["word"] == "природа"
        assert all_data["challenge"]["category"] in ["Временное ограничение", "Художественный стиль"]


@pytest.mark.integration
def test_user_timer_interaction(client, db_session, clean_db):
    """
    Тест сценария с таймером для временных ограничений:
    1. Пользователь получает задание с ограничением времени
    2. Использует таймер на странице
    """
    # Создаем временное задание
    from app.models import ChallengeCategory, Challenge

    time_category = ChallengeCategory(name="Временное ограничение")
    db_session.add(time_category)
    db_session.flush()

    time_challenge = Challenge(
        name="1 минута",
        description="1",
        category_id=time_category.id
    )
    db_session.add(time_challenge)
    db_session.commit()

    # Мокаем внешние API
    with patch('app.main.requests.get') as mock_requests, \
            patch('app.main.get_random_word') as mock_word:
        # Настройка моков
        mock_color_response = Mock()
        mock_color_response.status_code = 200
        mock_color_response.json.return_value = {
            'name': {'value': 'Sunset Orange'},
            'hex': {'value': '#FD5E53'}
        }
        mock_requests.return_value = mock_color_response
        mock_word.return_value = "спринт"

        # Получаем данные через API
        response = client.get("/api/random-all")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем, что получено временное задание
        assert data["challenge"]["category"] == "Временное ограничение"
        assert data["challenge"]["name"] == "1 минута"
        assert data["challenge"]["description"] == "1"


@pytest.mark.integration
def test_user_persistent_session_flow(client, db_session, clean_db):
    """
    Тест сценария работы в рамках одной сессии:
    Пользователь многократно генерирует комбинации для поиска вдохновения
    """
    # Создаем разнообразные данные
    from app.models import ChallengeCategory, Challenge

    categories = [
        ChallengeCategory(name="Временное ограничение"),
        ChallengeCategory(name="Художественный стиль"),
        ChallengeCategory(name="Композиция рисунка")
    ]
    db_session.add_all(categories)
    db_session.flush()

    challenges = []
    for i, category in enumerate(categories):
        for j in range(3):
            challenge = Challenge(
                name=f"Задание {i}-{j}",
                description=f"Описание {i}-{j}",
                category_id=category.id
            )
            challenges.append(challenge)
    db_session.add_all(challenges)
    db_session.commit()

    # Собираем результаты нескольких генераций
    all_results = []

    with patch('app.main.requests.get') as mock_requests, \
            patch('app.main.get_random_word') as mock_word:

        # Создаем последовательность цветов и слов
        colors = [
            {'name': 'Color 1', 'hex': '#FF0000'},
            {'name': 'Color 2', 'hex': '#00FF00'},
            {'name': 'Color 3', 'hex': '#0000FF'}
        ]

        words = ['слово1', 'слово2', 'слово3']

        # 3 раза генерируем полные комбинации
        for i in range(3):
            # Настройка моков для текущей итерации
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'name': {'value': colors[i]['name']},
                'hex': {'value': colors[i]['hex']}
            }
            mock_requests.return_value = mock_response
            mock_word.return_value = words[i]

            response = client.get("/api/random-all")
            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            all_results.append(data)

            # Проверяем, что каждый раз разные данные
            assert data["color"]["name"] == colors[i]['name']
            assert data["word"] == words[i]
            assert "challenge" in data
            assert data["challenge"]["category"] in ["Временное ограничение",
                                                     "Художественный стиль",
                                                     "Композиция рисунка"]

    # Убеждаемся, что получили разные комбинации
    assert len(all_results) == 3
    assert all_results[0]["color"]["hex"] != all_results[1]["color"]["hex"]
    assert all_results[0]["word"] != all_results[1]["word"]


@pytest.mark.integration
def test_health_check_flow(client):
    """
    Тест сценария проверки работоспособности системы
    """
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK

    health_data = response.json()
    assert health_data["status"] == "healthy"
    assert health_data["service"] == "Triple Generator"
    assert "timestamp" in health_data