import sqlite3
import os
import hashlib
from werkzeug.security import generate_password_hash

# Путь к директории с базой данных
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/instance')
DB_PATH = os.path.join(DB_DIR, 'patp.db')

# Создание директории, если её нет
os.makedirs(DB_DIR, exist_ok=True)

# Создание базы данных и таблиц
def init_db():
    # Подключение к базе данных
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создание таблицы пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание таблицы новостей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        image TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание таблицы обратной связи
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание таблицы заказов услуг
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        telephone TEXT NOT NULL,
        service_type TEXT NOT NULL,
        subject TEXT,
        message TEXT NOT NULL,
        is_processed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание таблицы заявок на работу
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS work_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        telephone TEXT NOT NULL,
        email TEXT,
        age TEXT,
        vacancy_type TEXT NOT NULL,
        experience TEXT,
        education TEXT,
        driving_license TEXT,
        message TEXT,
        resume_file TEXT,
        status TEXT DEFAULT 'Новая',
        is_processed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание администратора по умолчанию
    admin_username = 'admin'
    admin_password = 'admin123'  # В реальном проекте используйте сложный пароль
    
    # Проверка, существует ли уже администратор
    cursor.execute('SELECT * FROM users WHERE username = ?', (admin_username,))
    if not cursor.fetchone():
        # Хеширование пароля
        hashed_password = generate_password_hash(admin_password)
        
        # Добавление администратора
        cursor.execute(
            'INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)',
            (admin_username, hashed_password)
        )
    
    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()
    
    print(f"База данных инициализирована по пути: {DB_PATH}")

if __name__ == "__main__":
    init_db()