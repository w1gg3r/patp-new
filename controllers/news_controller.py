from flask import Blueprint, render_template, request
from config.database import get_db_connection

# Создаём blueprint для новостей
news_bp = Blueprint('news', __name__)

# Единая функция для /news и /news/page/<int:page>
@news_bp.route('/news')
@news_bp.route('/news/page/<int:page>')
def news_list(page=1):
    per_page = 9  # количество новостей на странице
    offset = (page - 1) * per_page

    conn = get_db_connection()
    
    # Получаем новости для текущей страницы
    news = conn.execute(
        'SELECT * FROM news ORDER BY created_at DESC LIMIT ? OFFSET ?', 
        (per_page, offset)
    ).fetchall()
    
    # Получаем общее количество новостей
    total_news = conn.execute('SELECT COUNT(*) FROM news').fetchone()[0]
    conn.close()

    # Вычисляем общее количество страниц
    total_pages = (total_news + per_page - 1) // per_page  # округление вверх
    
    return render_template(
        'news/news_list.html',
        news=news,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total_news=total_news
    )

@news_bp.route('/news/<int:id>')
def news_detail(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM news WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if post is None:
        return "Новость не найдена", 404
    
    return render_template('news/single_news.html', post=post)