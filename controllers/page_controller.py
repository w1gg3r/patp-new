from flask import Blueprint, render_template
from config.database import get_db_connection

page_bp = Blueprint('page', __name__)

@page_bp.route('/page/<int:id>')
def page_detail(id):
    conn = get_db_connection()
    page = conn.execute('SELECT * FROM pages WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if page is None:
        return "Страница не найдена", 404

    return render_template(f'{page.type}.html', page=page)