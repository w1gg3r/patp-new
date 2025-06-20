from flask import Flask, render_template, g, request, redirect, url_for
from config.database import get_db_connection, get_latest_news
from controllers.news_controller import news_bp
from controllers.contact_controller import contact_bp
from controllers.admin_controller import admin_bp, login_required

app = Flask(__name__, template_folder='views', static_folder='static')
app.secret_key = 'your_secret_key_here'

# === Регистрация Blueprints ===
app.register_blueprint(news_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(admin_bp)

# === Переменные перед рендером ===
@app.before_request
def load_latest_news():
    """Загружает последние новости для всех страниц"""
    try:
        conn = get_db_connection()
        g.all_news = conn.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
        g.latest_news = get_latest_news(3)  # последние 3 новости
        conn.close()
    except Exception as e:
        # На случай ошибок БД — хотя бы не сломает сайт
        g.all_news = []
        g.latest_news = []

# === Страницы сайта ===
@app.route('/')
def index():
    return render_template('index.html', news=g.all_news, latest_news=g.latest_news)

@app.route('/service')
def service():
    return render_template('service/service.html')

@app.route('/service/custom')
def service_custom():
    return render_template('service/service_custom.html')

@app.route('/service/passenger')
def service_passenger():
    return render_template('service/service_passenger.html')

@app.route('/service/children')
def service_children():
    return render_template('service/service_children.html')

# === Новости ===
@app.route('/news')
def news_list():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    offset = (page - 1) * per_page

    try:
        conn = get_db_connection()
        news = conn.execute(
            'SELECT * FROM news ORDER BY created_at DESC LIMIT ? OFFSET ?', 
            (per_page, offset)
        ).fetchall()
        total_news = conn.execute('SELECT COUNT(*) FROM news').fetchone()[0]
        conn.close()
        
        total_pages = (total_news + per_page - 1) // per_page
        return render_template('news/news_list.html', news=news, page=page, total_pages=total_pages)
    except Exception as e:
        return render_template('error/404.html', error="Ошибка загрузки новостей"), 500

@app.route('/news/<int:id>')
def news_detail(id):
    try:
        conn = get_db_connection()
        post = conn.execute(
            'SELECT * FROM news WHERE id = ?', 
            (id,)
        ).fetchone()
        conn.close()

        if not post:
            return render_template('error/404.html', error="Новость не найдена"), 404

        return render_template('news/single_news.html', post=post)
    except Exception as e:
        return render_template('error/500.html', error=str(e)), 500

# === Контакты и форма заказа услуги ===
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        service_type = request.form.get('service_type')
        subject = request.form.get('subject')
        message = request.form.get('message')
        consent = request.form.get('consent')

        if not name or not email or not telephone or not service_type or not message or not consent:
            return render_template('contact.html', error="Пожалуйста, заполните все обязательные поля")

        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO service_orders (name, email, telephone, service_type, subject, message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, telephone, service_type, subject, message))
            conn.commit()
            conn.close()
            return render_template('contact.html', success="Ваша заявка успешно отправлена")
        except Exception as e:
            return render_template('contact.html', error=f"Ошибка: {str(e)}")

    return render_template('contact.html')

@app.route('/admin/orders')
def orders_list():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM service_orders').fetchall()
    conn.close()
    return render_template('admin/orders.html', orders=orders)

@app.route('/submit-order', methods=['POST'])
def submit_order():
    name = request.form.get('name')
    email = request.form.get('email')
    telephone = request.form.get('telephone')
    service_type = request.form.get('service_type')
    message = request.form.get('message')
    consent = request.form.get('consent')

    if not name:
        flash('Пожалуйста, укажите имя', 'danger')
        return redirect(url_for('contact'))

    if not service_type:
        flash('Пожалуйста, выберите услугу', 'danger')
        return redirect(url_for('contact'))

    if not message:
        flash('Пожалуйста, опишите услугу', 'danger')
        return redirect(url_for('contact'))

    if not consent:
        flash('Необходимо дать согласие на обработку данных', 'danger')
        return redirect(url_for('contact'))

    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO service_orders (name, email, telephone, service_type, subject, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, telephone, service_type, subject, message))
        conn.commit()
        conn.close()
        flash('Ваша заявка успешно отправлена!', 'success')
    except Exception as e:
        flash(f'Ошибка при отправке заявки: {str(e)}', 'danger')

    return redirect(url_for('contact'))

# === Обработка ошибок ===
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html', error=error), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error/500.html', error=error), 500

# === Запуск сервера ===
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)