import sqlite3
import os

# Путь к базе данных
db_path = os.path.join('../instance', 'patp.db')


test_data_sql = """
INSERT INTO news (title, content, image) VALUES
('Новая линия метро в Вологде', 'Городские власти объявили о запуске новой линии метро в 2026 году.', 'news-item-4.jpg'),
('Экологический форум', 'ПАТП №1 участвует в экологическом форуме по устойчивому транспорту.', 'news-item-5.jpg'),
('Расширение автопарка', 'Компания закупила 10 новых автобусов для перевозки школьников.', 'news-item-6.jpg'),
('Безопасность в дороге', 'Внедрены новые меры безопасности для пассажиров в ночных рейсах.', 'news-item-7.jpg'),
('Поддержка ветеранов', 'ПАТП №1 предоставляет бесплатные проезды для ветеранов в День Победы.', 'news-item-8.jpg'),
('Оптимизация маршрутов', 'С помощью AI-системы оптимизированы маршруты автобусов в часы пик.', 'news-item-9.jpg'),
('Сотрудничество с университетом', 'Заключён договор с Вологодским университетом на стажировки водителей.', 'news-item-10.jpg');
"""

cursor.executescript(test_data_sql)

def init_db():
    # Убедимся, что папка instance существует
    if not os.path.exists('instance'):
        os.makedirs('instance')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(create_news_sql)

    try:
        cursor.execute("SELECT COUNT(*) FROM news")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executescript(test_data_sql)
            print("✅ Таблица `news` создана и заполнена тестовыми данными.")
        else:
            print(f"ℹ️ В таблице `news` уже есть {count} записей.")
    except Exception as e:
        print("⚠️ Ошибка при проверке данных:", e)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()