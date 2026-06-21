import sqlite3

DB_NAME = "notes.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def add_note(title, content, created_at, tags_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)", (title, content, created_at))
    note_id = cursor.lastrowid
    
    for tag_name in tags_list:
        tag_name = tag_name.strip().lower()
        if not tag_name:
            continue
            
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = cursor.fetchone()['id']
        cursor.execute("INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)", (note_id, tag_id))
        
    conn.commit()
    conn.close()

def get_all_notes(search_query=None, filter_tag=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if filter_tag:
        cursor.execute('''
            SELECT n.* FROM notes n
            JOIN note_tags nt ON n.id = nt.note_id
            JOIN tags t ON nt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY n.id DESC
        ''', (filter_tag.lower(),))
    elif search_query:
        cursor.execute('''
            SELECT * FROM notes 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY id DESC
        ''', (f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("SELECT * FROM notes ORDER BY id DESC")
        
    notes = cursor.fetchall()
    
    result = []
    for note in notes:
        note_dict = dict(note)
        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN note_tags nt ON t.id = nt.tag_id
            WHERE nt.note_id = ?
        ''', (note_dict['id'],))
        note_dict['tags'] = [row['name'] for row in cursor.fetchall()]
        result.append(note_dict)
        
    conn.close()
    return result

def get_all_tags():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM tags ORDER BY name ASC")
    tags = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return tags

def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
    cursor.execute("DELETE FROM tags WHERE id NOT IN (SELECT DISTINCT tag_id FROM note_tags)")
    conn.commit()
    conn.close()