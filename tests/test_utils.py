import pytest
from app.main import get_random_color, get_random_word
from unittest.mock import patch, Mock


def test_get_random_word():
    """Тест генерации случайного слова"""
    word = get_random_word()

    assert isinstance(word, str)
    assert len(word) > 0
    # Русское слово должно содержать кириллические символы
    assert any('\u0400' <= char <= '\u04FF' for char in word)


@patch('app.main.requests.get')
def test_get_random_color_success(mock_get):
    """Тест успешного получения цвета"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'name': {'value': 'Test Red'},
        'hex': {'value': '#FF0000'}
    }
    mock_get.return_value = mock_response

    color = get_random_color()

    assert color['name'] == 'Test Red'
    assert color['hex'] == '#FF0000'
    mock_get.assert_called_once_with('https://www.thecolorapi.com/random', timeout=3)


@patch('app.main.requests.get')
def test_get_random_color_invalid_response(mock_get):
    """Тест невалидного ответа от сервиса цветов"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'invalid': 'data'}  # Нет нужных полей
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="Некорректный ответ от сервиса цветов"):
        get_random_color()