from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import database

app = Flask(__name__)
app.secret_key = 'super-secret-notes-key-9876'

# Инициализируем базу данных при старте
database.init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    filter_tag = request.args.get('tag', '').strip()
    
    # Получаем заметки в зависимости от фильтра или поиска
    if filter_tag:
        notes = database.get_all_notes(filter_tag=filter_tag)
    elif search_query:
        notes = database.get_all_notes(search_query=search_query)
    else:
        notes = database.get_all_notes()
        
    # Получаем список вообще всех тегов для боковой панели ("Облако тегов")
    all_tags = database.get_all_tags()
    
    return render_template('index.html', notes=notes, all_tags=all_tags, search_query=search_query, current_tag=filter_tag)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    tags_raw = request.form.get('tags', '').strip()
    
    if not title or not content:
        # Простая валидация: заголовок и текст не должны быть пустыми
        return redirect(url_for('index'))
        
    # Разбиваем строку с тегами по запятым и убираем лишние пробелы
    tags_list = [tag.strip() for tag in tags_raw.split(',') if tag.strip()]
    
    created_at = datetime.now().strftime("%d.%m.%Y в %H:%M")
    database.add_note(title, content, created_at, tags_list)
    
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>')
def delete(note_id):
    database.delete_note(note_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)