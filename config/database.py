import sqlite3
import os

def get_db_connection():
    db_path = os.path.join('config', 'instance', 'patp.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_latest_news(limit=3):
    conn = get_db_connection()
    news = conn.execute(
        'SELECT * FROM news ORDER BY created_at DESC LIMIT ?', 
        (limit,)
    ).fetchall()
    conn.close()
    return news