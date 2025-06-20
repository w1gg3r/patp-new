from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_from_directory
from config.database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename 
from functools import wraps
import os


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# === Декоратор login_required ===
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Сначала войдите в систему', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return wrap

# === Маршрут: /admin/login ===
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))

        # === Отправляем сообщение о неверных данных ===
        flash('Неверный логин или пароль', 'danger')
        return redirect(url_for('admin.login'))

    return render_template('admin/login.html')

# === Маршрут: /admin/logout ===
@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    
    # Удаляем все сообщения, кроме 'logout'
    session['_flashes'] = [
        (cat, msg) for (cat, msg) in session.get('_flashes', [])
        if cat == 'logout'
    ]

    # Добавляем сообщение о выходе, если его нет
    if not any(cat == 'logout' for (cat, msg) in session.get('_flashes', [])):
        flash('Вы вышли из системы', 'logout')

    return redirect(url_for('index'))  # ← Редирект на главную

# === Маршрут: /admin/dashboard ===
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# === Маршрут: /admin/news ===
@admin_bp.route('/news')
@login_required
def news_list():
    conn = get_db_connection()
    news = conn.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/news.html', news=news)

# === Маршрут: /admin/news/add ===
@admin_bp.route('/news/add', methods=['GET', 'POST'])
@login_required
def news_add():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')  # Получаем файл

        if not title or not content:
            flash('Заголовок и текст обязательны', 'danger')
            return redirect(url_for('admin.news_add'))

        # Обработка изображения
        image_name = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_name = filename

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO news (title, content, image) VALUES (?, ?, ?)',
            (title, content, image_name)
        )
        conn.commit()
        conn.close()

        flash('Новость добавлена', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_add.html')

@admin_bp.route('/news/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM news WHERE id = ?', (id,)).fetchone()
    conn.close()

    if not post:
        flash('Новость не найдена', 'danger')
        return redirect(url_for('admin.news_list'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        if not title or not content:
            flash('Заголовок и текст обязательны', 'danger')
            return redirect(url_for('admin.news_edit', id=id))

        # Обработка изображения
        image_name = post['image']
        if image and image.filename:
            filename = secure_filename(image.filename)  # <--- Теперь работает
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_name = filename

        conn = get_db_connection()
        conn.execute('UPDATE news SET title = ?, content = ?, image = ? WHERE id = ?', 
                    (title, content, image_name, id))
        conn.commit()
        conn.close()

        flash('Новость обновлена', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_edit.html', post=post)

# === Маршрут: /admin/news/<id>/delete ===
@admin_bp.route('/news/<int:id>/delete', methods=['POST'])
@login_required
def news_delete(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM news WHERE id = ?', (id,)).fetchone()
    
    if not post:
        flash('Новость не найдена', 'danger')
        return redirect(url_for('admin.news_list'))

    conn.execute('DELETE FROM news WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Новость удалена', 'success')
    return redirect(url_for('admin.news_list'))

# === Маршрут: /admin/feedback ===
@admin_bp.route('/feedback')
@login_required
def feedback_list():
    conn = get_db_connection()
    feedback = conn.execute('SELECT * FROM feedback ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/feedback.html', feedback=feedback)

# === Маршрут: /feedback/<int:id>/update-status ===
@admin_bp.route('/feedback/<int:id>/update-status', methods=['POST'])
@login_required
def feedback_update_status(id):
    new_status = request.form.get('status')
    if new_status not in ['Новая', 'В обработке', 'Выполнено', 'Отклонено']:
        flash('Некорректный статус', 'danger')
        return redirect(url_for('admin.feedback_list'))

    conn = get_db_connection()
    conn.execute('UPDATE feedback SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()

    flash(f'Статус заявки №{id} изменён на "{new_status}"', 'success')
    return redirect(url_for('admin.feedback_list'))

# === Маршрут: /admin/feedback/<id>/delete ===
@admin_bp.route('/feedback/<int:id>/delete', methods=['POST'])
@login_required
def feedback_delete(id):
    conn = get_db_connection()
    msg = conn.execute('SELECT * FROM feedback WHERE id = ?', (id,)).fetchone()
    
    if not msg:
        flash('Заявка не найдена', 'danger')
        return redirect(url_for('admin.feedback_list'))

    conn.execute('DELETE FROM feedback WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Заявка удалена', 'success')
    return redirect(url_for('admin.feedback_list'))

    

@admin_bp.route('/orders')
@login_required
def orders_list():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM service_orders ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/order/<int:id>/update-status', methods=['POST'])
@login_required
def order_update_status(id):
    new_status = request.form.get('status')
    if new_status not in ['Новая', 'В обработке', 'Выполнено', 'Отклонено']:
        flash('Некорректный статус', 'danger')
        return redirect(url_for('admin.orders_list'))

    conn = get_db_connection()
    conn.execute('UPDATE service_orders SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()

    flash(f'Статус заявки №{id} изменён на "{new_status}"', 'success')
    return redirect(url_for('admin.orders_list'))

@admin_bp.route('/order/<int:id>/delete', methods=['POST'])
@login_required
def order_delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM service_orders WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Заявка удалена', 'success')
    return redirect(url_for('admin.orders_list'))

# === Для тестирования: добавьте временный маршрут для проверки хэша ===
@admin_bp.route('/test-login')
def test_login():
    # Этот маршрут временно добавляет тестового админа с паролем "admin"
    conn = get_db_connection()
    test_password = generate_password_hash("admin")
    conn.execute('INSERT OR IGNORE INTO admins (username, password_hash) VALUES (?, ?)', ("admin", test_password))
    conn.commit()
    conn.close()
    flash('Тестовый админ добавлен или уже существует', 'success')
    return redirect(url_for('admin.login'))