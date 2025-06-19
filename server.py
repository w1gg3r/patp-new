from flask import Flask, render_template
from config.database import get_latest_news, get_db_connection  # ✅ Добавлен импорт
from controllers.news_controller import news_bp  # Импорт Blueprint новостей

# Создаем Flask-приложение
app = Flask(__name__, template_folder='views')

# Регистрация blueprint'а
app.register_blueprint(news_bp)

# Маршрут: Главная страница
@app.route('/')
def index():
    # Получаем ВСЕ новости из БД
    conn = get_db_connection()
    all_news = conn.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', latest_news=all_news)
    
# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True)