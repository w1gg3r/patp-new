from flask import Blueprint, render_template, g
from config.database import get_db_connection

route_bp = Blueprint('route', __name__)

@route_bp.route('/routes')
def route_list():
    conn = get_db_connection()
    routes = conn.execute('SELECT * FROM routes ORDER BY route_number').fetchall()
    conn.close()
    return render_template('routes/route_list.html', routes=routes, latest_news=g.latest_news)

@route_bp.route('/routes/<int:id>')
def route_detail(id):
    conn = get_db_connection()
    route = conn.execute('SELECT * FROM routes WHERE id = ?', (id,)).fetchone()
    conn.close()
    if route is None:
        return "Маршрут не найден", 404
    return render_template('routes/route_detail.html', route=route, latest_news=g.latest_news)