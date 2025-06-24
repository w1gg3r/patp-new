from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_from_directory, g
from config.database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename 
from functools import wraps
import os


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Указываем абсолютный путь к директории для загрузки файлов
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Проверяем права доступа к директории
if not os.access(UPLOAD_FOLDER, os.W_OK):
    print(f"ВНИМАНИЕ: Нет прав на запись в директорию {UPLOAD_FOLDER}")

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        # Проверка на наличие логина и пароля
        if not username or not password:
            flash('Пожалуйста, введите логин и пароль', 'danger')
            return redirect(url_for('admin.login'))

        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))

        # === Отправляем сообщение о неверных данных ===
        flash('Неверный логин или пароль', 'danger')
        return redirect(url_for('admin.login'))

    return render_template('admin/login.html', latest_news=g.latest_news)

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
    return render_template('admin/dashboard.html', latest_news=g.latest_news)

# === Маршрут: /admin/news ===
@admin_bp.route('/news')
@login_required
def news_list():
    conn = get_db_connection()
    news = conn.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/news.html', news=news, latest_news=g.latest_news)

# === Маршрут: /admin/news/add ===
@admin_bp.route('/news/add', methods=['GET', 'POST'])
@login_required
def news_add():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        # Проверяем, что форма содержит файл
        if 'image' not in request.files:
            flash('Не найдено поле для загрузки файла', 'warning')
            return redirect(request.url)
            
        image = request.files['image']
        
        # Если пользователь не выбрал файл, браузер может отправить пустое поле
        if image.filename == '':
            flash('Изображение не выбрано', 'warning')
        
        if not title or not content:
            flash('Заголовок и текст обязательны', 'danger')
            return redirect(url_for('admin.news_add'))

        # Обработка изображения
        image_name = None
        if image and image.filename and allowed_file(image.filename):
            try:
                filename = secure_filename(image.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(file_path)
                image_name = filename
                flash(f'Изображение {filename} успешно загружено', 'success')
            except Exception as e:
                flash(f'Ошибка при загрузке изображения: {str(e)}', 'danger')
        elif image and image.filename:
            flash('Недопустимый формат файла. Разрешены: png, jpg, jpeg, gif', 'warning')

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO news (title, content, image) VALUES (?, ?, ?)',
            (title, content, image_name)
        )
        conn.commit()
        conn.close()

        flash('Новость добавлена', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_add.html', latest_news=g.latest_news)

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
        
        if not title or not content:
            flash('Заголовок и текст обязательны', 'danger')
            return redirect(url_for('admin.news_edit', id=id))

        # Сохраняем текущее изображение
        image_name = post['image']
        
        # Проверяем наличие загруженного файла
        if 'image' in request.files:
            image = request.files['image']
            
            # Если загружен новый файл
            if image and image.filename:
                if allowed_file(image.filename):
                    try:
                        filename = secure_filename(image.filename)
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        image.save(file_path)
                        image_name = filename
                        flash(f'Изображение {filename} успешно загружено', 'success')
                    except Exception as e:
                        flash(f'Ошибка при загрузке изображения: {str(e)}', 'danger')
                else:
                    flash('Недопустимый формат файла. Разрешены: png, jpg, jpeg, gif', 'warning')

        conn = get_db_connection()
        conn.execute('UPDATE news SET title = ?, content = ?, image = ? WHERE id = ?', 
                    (title, content, image_name, id))
        conn.commit()
        conn.close()

        flash('Новость обновлена', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_edit.html', post=post, latest_news=g.latest_news)

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
    return render_template('admin/feedback.html', feedback=feedback, latest_news=g.latest_news)

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

@admin_bp.route('/work-applications')
@login_required
def work_applications_list():
    conn = get_db_connection()
    applications = conn.execute('SELECT * FROM work_applications ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/work_applications.html', applications=applications, latest_news=g.latest_news)

@admin_bp.route('/work-application/<int:id>/update-status', methods=['POST'])
@login_required
def work_application_update_status(id):
    new_status = request.form.get('status')
    if new_status not in ['Новая', 'В обработке', 'Собеседование', 'Принят', 'Отклонено']:
        flash('Некорректный статус', 'danger')
        return redirect(url_for('admin.work_applications_list'))

    conn = get_db_connection()
    conn.execute('UPDATE work_applications SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()

    flash(f'Статус заявки №{id} изменён на "{new_status}"', 'success')
    return redirect(url_for('admin.work_applications_list'))

@admin_bp.route('/work-application/<int:id>/delete', methods=['POST'])
@login_required
def work_application_delete(id):
    conn = get_db_connection()
    # Получаем информацию о заявке, чтобы удалить файл резюме, если он есть
    application = conn.execute('SELECT * FROM work_applications WHERE id = ?', (id,)).fetchone()
    
    if not application:
        flash('Заявка не найдена', 'danger')
        return redirect(url_for('admin.work_applications_list'))
    
    # Удаляем файл резюме, если он существует
    if application['resume_file']:
        resume_path = os.path.join(UPLOAD_FOLDER, application['resume_file'])
        if os.path.exists(resume_path):
            try:
                os.remove(resume_path)
            except Exception as e:
                print(f"Ошибка при удалении файла: {e}")
    
    # Удаляем заявку из базы данных
    conn.execute('DELETE FROM work_applications WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Заявка удалена', 'success')
    return redirect(url_for('admin.work_applications_list'))

# Корневой маршрут /admin
@admin_bp.route('/')
def admin_index():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))