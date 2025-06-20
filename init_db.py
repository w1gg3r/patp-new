import sqlite3
import os

# Путь к базе данных
db_path = os.path.join('config', 'instance', 'patp.db')

# SQL-запросы для создания таблиц
create_news_sql = """
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_feedback_sql = """
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    telephone TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    consent BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_admin_sql = """
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# === Добавьте SQL-запрос ===
create_service_orders_sql = """
CREATE TABLE IF NOT EXISTS service_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    telephone TEXT NOT NULL,
    service_type TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Новая',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db():
    # ... другие таблицы ...

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Добавьте новую таблицу
    cursor.execute(create_service_orders_sql)

    # Проверка и добавление тестового заказа (по желанию)
    cursor.execute("SELECT COUNT(*) FROM service_orders")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute(
            "INSERT INTO service_orders (name, email, telephone, service_type, message) VALUES (?, ?, ?, ?, ?)",
            ("Иван Иванов", "ivan@example.com", "+79112223344", "Заказной трансфер", "Нужен автобус на 20 человек 10 апреля")
        )

    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    init_db()