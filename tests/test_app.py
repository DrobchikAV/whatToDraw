import pytest
from unittest.mock import patch, AsyncMock, Mock
from fastapi import status
import json

def test_api_random_color(client, mock_requests, sample_color_data):
    """Тест API для получения случайного цвета"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_color_data
    mock_requests.get.return_value = mock_response

    response = client.get("/api/random-color")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Test Blue"
    assert response.json()["hex"] == "#0000FF"

def test_api_random_word(client):
    """Тест API для получения случайного слова"""
    with patch('app.main.get_random_word', return_value="тестовое_слово"):
        response = client.get("/api/random-word")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["word"] == "тестовое_слово"


def test_api_random_challenge(client, db_session, sample_challenge_data):
    """Тест API для получения случайного усложнения"""
    response = client.get("/api/random-challenge")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "category" in data
    assert "name" in data
    assert "description" in data
    assert data["category"] == "Test Category"
    assert data["name"] == "Test Challenge"
    assert data["description"] == "Test Description"


def test_api_random_all(client, mock_requests, db_session, sample_challenge_data):
    """Тест API для получения всех трех случайных значений"""
    # Мокаем ответ от color API
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'name': {'value': 'Test Color'},
        'hex': {'value': '#FF0000'}
    }
    mock_requests.get.return_value = mock_response

    # Мокаем get_random_word
    with patch('app.main.get_random_word', return_value="тестовое_слово"):
        response = client.get("/api/random-all")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "color" in data
    assert "word" in data
    assert "challenge" in data

    assert data["color"]["name"] == "Test Color"
    assert data["color"]["hex"] == "#FF0000"
    assert data["word"] == "тестовое_слово"
    assert data["challenge"]["category"] == "Test Category"