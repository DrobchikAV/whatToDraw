import pytest
from unittest.mock import patch, mock_open, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from app.crud import (
    get_random_challenge,
    load_data_from_file,
    create_initial_data,
    get_data_file_path
)
from app.models import Challenge, ChallengeCategory


def test_get_random_challenge_empty_db(db_session, clean_db):
    # Убедимся, что БД пуста
    assert db_session.query(Challenge).count() == 0

    # Функция должна вернуть None или вызвать исключение
    try:
        result = get_random_challenge(db_session)
        assert result is None   # Если не было исключения, то None
    except Exception as e:
        # Если искл, то проверка, что это ожидаемое исключение
        assert "Нет доступных усложнений" in str(e) or "404" in str(e)


def test_get_random_challenge_with_data(db_session, sample_challenge_data):
    """Тест получения случайного усложнения с данными"""
    result = get_random_challenge(db_session)

    assert result is not None
    assert isinstance(result, dict)
    assert "category" in result
    assert "challenge" in result
    assert result["category"].name == "Test Category"
    assert result["challenge"].name == "Test Challenge"
    assert result["challenge"].description == "Test Description"


def test_get_random_challenge_multiple(db_session, clean_db):
    """Тест получения случайного усложнения из нескольких записей"""
    # Создаем несколько категорий и заданий
    category1 = ChallengeCategory(name="Category 1")
    category2 = ChallengeCategory(name="Category 2")
    db_session.add_all([category1, category2])
    db_session.flush()

    challenges = []
    for i in range(5):
        challenge = Challenge(
            name=f"Challenge {i}",
            description=f"Description {i}",
            category_id=category1.id if i % 2 == 0 else category2.id
        )
        challenges.append(challenge)

    db_session.add_all(challenges)
    db_session.commit()

    # Получаем случайное задание несколько раз
    results = set()
    for _ in range(10):
        result = get_random_challenge(db_session)
        if result:
            results.add(result["challenge"].name)

    # Должны получить хотя бы несколько разных результатов
    assert len(results) > 1


def test_load_data_from_file():
    """Тест загрузки данных из файла"""
    mock_file_content = """Категория: Тестовая категория
- Задание 1: Описание задания 1
- Задание 2: Описание задания 2
"""

    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        with patch('os.path.exists', return_value=True):
            data = load_data_from_file("dummy_path.txt")

    assert len(data) == 1
    assert data[0]['name'] == 'Тестовая категория'
    assert len(data[0]['challenges']) == 2
    assert data[0]['challenges'][0]['name'] == 'Задание 1'
    assert data[0]['challenges'][0]['description'] == 'Описание задания 1'


def test_load_data_from_file_with_multiple_categories():
    """Тест загрузки данных с несколькими категориями"""
    mock_file_content = """Категория: Категория 1
- Задание 1: Описание 1

Категория: Категория 2
- Задание 2: Описание 2
- Задание 3: Описание 3
"""

    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        with patch('os.path.exists', return_value=True):
            data = load_data_from_file("dummy_path.txt")

    assert len(data) == 2
    assert data[0]['name'] == 'Категория 1'
    assert data[1]['name'] == 'Категория 2'
    assert len(data[0]['challenges']) == 1
    assert len(data[1]['challenges']) == 2


def test_load_data_from_file_empty_lines():
    """Тест загрузки данных с пустыми строками"""
    mock_file_content = """
Категория: Тестовая категория

- Задание 1: Описание задания 1

- Задание 2: Описание задания 2

"""

    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        with patch('os.path.exists', return_value=True):
            data = load_data_from_file("dummy_path.txt")

    assert len(data) == 1
    assert len(data[0]['challenges']) == 2


def test_load_data_from_file_not_found():
    """Тест обработки отсутствующего файла"""
    with patch('os.path.exists', return_value=False):
        with pytest.raises(FileNotFoundError):
            load_data_from_file("non_existent.txt")


def test_create_initial_data_already_exists(db_session, sample_challenge_data):
    """Тест инициализации данных, когда они уже есть"""
    initial_count = db_session.query(Challenge).count()

    # Функция должна ничего не делать
    with patch('app.crud.load_data_from_file') as mock_load:
        create_initial_data(db_session)
        mock_load.assert_not_called()

    # Количество записей не должно измениться
    assert db_session.query(Challenge).count() == initial_count


def test_create_initial_data_new(db_session, clean_db):
    """Тест инициализации данных в пустой БД"""
    mock_data = [
        {
            'name': 'Test Category 1',
            'challenges': [
                {'name': 'Challenge 1', 'description': 'Desc 1'},
                {'name': 'Challenge 2', 'description': 'Desc 2'}
            ]
        },
        {
            'name': 'Test Category 2',
            'challenges': [
                {'name': 'Challenge 3', 'description': 'Desc 3'}
            ]
        }
    ]

    with patch('app.crud.load_data_from_file', return_value=mock_data):
        create_initial_data(db_session)

    # Проверяем, что данные созданы
    categories = db_session.query(ChallengeCategory).all()
    challenges = db_session.query(Challenge).all()

    assert len(categories) == 2
    assert len(challenges) == 3

    category_names = [c.name for c in categories]
    assert 'Test Category 1' in category_names
    assert 'Test Category 2' in category_names


@patch.dict('os.environ', {'DATA_FILE': '/path/to/test_data.txt'})
def test_get_data_file_path_from_env():
    """Тест получения пути к файлу данных из переменной окружения"""
    with patch('os.path.exists', return_value=True):
        result = get_data_file_path()
        assert result == '/path/to/test_data.txt'


@patch.dict('os.environ', {'DATA_FILE': ''})
def test_get_data_file_path_no_env():
    """Тест получения пути к файлу данных без переменной окружения"""
    with pytest.raises(ValueError, match="Переменная окружения DATA_FILE не установлена"):
        get_data_file_path()