from flask import Blueprint, render_template, request
from config.database import get_db_connection

# Создаём blueprint для новостей
news_bp = Blueprint('news', __name__)

# === Список новостей с обработкой отсутствующих изображений ===
@news_bp.route('/news')
@news_bp.route('/news/page/<int:page>')
def news_list(page=1):
    per_page = 9
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    # Используем COALESCE для замены NULL на placeholder.png
# В `news_controller.py`
    news = conn.execute('''
        SELECT id, title, content, created_at, COALESCE(image, 'placeholder.png') AS image 
        FROM news 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    
    total_news = conn.execute('SELECT COUNT(*) FROM news').fetchone()[0]
    conn.close()
    
    total_pages = (total_news + per_page - 1) // per_page
    return render_template(
        'news/news_list.html',
        news=news,
        page=page,
        total_pages=total_pages
    )

# === Детализация новости с защитой от отсутствующего изображения ===
@news_bp.route('/news/<int:id>')
def news_detail(id):
    conn = get_db_connection()
    # Используем COALESCE, чтобы image всегда был строкой
    post = conn.execute('''
        SELECT 
            id, 
            title, 
            content, 
            created_at,
            COALESCE(image, 'placeholder.png') AS image
        FROM news 
        WHERE id = ?
    ''', (id,)).fetchone()
    conn.close()
    
    if post is None:
        return "Новость не найдена", 404
    
    return render_template('news/single_news.html', post=post)