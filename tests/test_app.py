import pytest
from app import app
import database

@pytest.fixture
def client():
    app.config['TESTING'] = True
    database.init_db()
    with app.test_client() as client:
        yield client

def test_index_page(client):
    # 1. Тест главной страницы (код ответа 200)
    response = client.get('/')
    assert response.status_code == 200

def test_add_note(client):
    # 2. Тест добавления заметки в БД
    response = client.post('/add', data={
        'title': 'Тестовая заметка',
        'content': 'Текст тестовой заметки',
        'tags': 'тест, pytest'
    })
    assert response.status_code == 302  # Редирект после успешного добавления
    
    # Проверяем, что заметка действительно появилась в базе данных
    notes = database.get_all_notes()
    assert len(notes) > 0
    assert notes[0]['title'] == 'Тестовая заметка'
    assert 'тест' in notes[0]['tags']

def test_search_and_filter(client):
    # 3. Тест поиска/фильтрации по тегу или тексту
    database.add_note('СпецифичныйЗаголовок', 'Содержимое', '21.06.2026', ['уникальный_тег'])
    
    # Проверяем поиск по слову
    notes_search = database.get_all_notes(search_query='Специфичный')
    assert len(notes_search) == 1
    
    # Проверяем фильтрацию по тегу
    notes_tag = database.get_all_notes(filter_tag='уникальный_тег')
    assert len(notes_tag) == 1

def test_empty_validation(client):
    # 4. Тест валидации: пустое поле должно отклоняться (редирект без добавления в БД)
    notes_before = len(database.get_all_notes())
    
    response = client.post('/add', data={
        'title': '',
        'content': 'Текст без заголовка',
        'tags': ''
    })
    
    notes_after = len(database.get_all_notes())
    assert notes_before == notes_after  # Количество записей не должно измениться