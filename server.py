from flask import Flask, render_template, g, request, redirect, url_for, flash, jsonify, session, send_from_directory
from config.database import get_db_connection, get_latest_news
from controllers.news_controller import news_bp
from controllers.contact_controller import contact_bp
from controllers.admin_controller import admin_bp, login_required
import os
from werkzeug.utils import secure_filename
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__, template_folder='views', static_folder='static')
app.secret_key = 'your_secret_key'

# Middleware для добавления заголовков CSP
@app.after_request
def add_security_headers(response):
    # Разрешаем загрузку скриптов из внешних источников
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; img-src 'self' data:;"
    return response

# Настройка загрузки файлов
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Регистрация blueprints
app.register_blueprint(news_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(admin_bp)

# === Загрузка последних новостей перед каждым запросом ===
@app.before_request
def before_request():
    g.latest_news = get_latest_news(3)

# === Главная страница ===
@app.route('/')
def index():
    conn = get_db_connection()
    news = conn.execute('SELECT * FROM news ORDER BY created_at DESC LIMIT 10').fetchall()
    conn.close()
    return render_template('index.html', news=news, latest_news=g.latest_news)

# === О нас ===
@app.route('/about')
def about():
    return render_template('about-us/about-company.html', latest_news=g.latest_news)

# === Расписание ===
@app.route('/schedule')
def schedule():
    return render_template('schedule.html', latest_news=g.latest_news)

# === Услуги ===
@app.route('/service')
def service():
    return render_template('service/service.html', latest_news=g.latest_news)

@app.route('/service/passenger')
def service_passenger():
    return render_template('service/service_passenger.html', latest_news=g.latest_news)

@app.route('/service/children')
def service_children():
    return render_template('service/service_children.html', latest_news=g.latest_news)

@app.route('/service/custom')
def service_custom():
    return render_template('service/service_custom.html', latest_news=g.latest_news)

@app.route('/service_order')
def service_order():
    return render_template('service_order.html', latest_news=g.latest_news)

# === Маршруты ===
@app.route('/routes')
def routes():
    return render_template('routes/route_list.html', latest_news=g.latest_news)

@app.route('/routes/<int:route_id>')
def route_detail(route_id):
    return render_template('routes/route_detail.html', route_id=route_id, latest_news=g.latest_news)

# === Автопарк ===
@app.route('/autopark')
def autopark():
    return render_template('about-us/autopark.html', latest_news=g.latest_news)

# === Официальная информация ===
@app.route('/official-information')
def official_information():
    return render_template('official-info/official-information.html', latest_news=g.latest_news)

# === Антикоррупция ===
@app.route('/anti-corruption')
def anti_corruption():
    return render_template('about-us/anti-corruption.html', latest_news=g.latest_news)

# === Документы ===
@app.route('/documents')
def documents():
    return render_template('about-us/documents.html', latest_news=g.latest_news)

# === Информация от прокуратуры ===
@app.route('/info-for-police-vologda')
def info_for_police():
    return render_template('official-info/info-for-police-vologda.html', latest_news=g.latest_news)

# === Оплата проезда ===
@app.route('/payment')
def payment():
    return render_template('payment/payment.html', latest_news=g.latest_news)

@app.route('/price')
def price():
    return render_template('payment/price.html', latest_news=g.latest_news)

# === Работа у нас ===
@app.route('/work')
def work():
    return render_template('work/work.html', latest_news=g.latest_news)

@app.route('/work_order')
def work_order():
    return render_template('work/work_order.html', latest_news=g.latest_news)

# === Контакты ===
@app.route('/contact')
def contact():
    return render_template('about-us/contact.html', latest_news=g.latest_news)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if not name or not email or not message:
        flash('Пожалуйста, заполните все поля', 'danger')
        return redirect(url_for('contact'))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO feedback (name, email, message, created_at) VALUES (?, ?, ?, datetime("now"))',
                (name, email, message))
    conn.commit()
    conn.close()
    
    flash('Ваше сообщение успешно отправлено!', 'success')
    return redirect(url_for('contact'))

@app.route('/submit-order', methods=['POST'])
def submit_order():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        service_type = request.form.get('service_type')
        subject = request.form.get('subject', '')
        message = request.form.get('message')
        
        # Проверка согласия на обработку данных
        if not request.form.get('consent'):
            flash('Необходимо дать согласие на обработку персональных данных', 'danger')
            return redirect(url_for('service_order'))
        
        # Проверка обязательных полей
        if not name or not email or not telephone or not service_type or not message:
            flash('Пожалуйста, заполните все обязательные поля', 'danger')
            return redirect(url_for('service_order'))
        
        # Сохранение в базу данных
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO service_orders (name, email, telephone, service_type, subject, message, status, is_processed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (name, email, telephone, service_type, subject, message, 'Новая', 0))
        conn.commit()
        conn.close()
        
        flash('Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('service_order'))
    except Exception as e:
        print(f"Error in submit_order: {e}")
        flash('Произошла ошибка при отправке заявки. Пожалуйста, попробуйте еще раз позже.', 'danger')
        return redirect(url_for('service_order'))

@app.route('/submit-work-order', methods=['POST'])
def submit_work_order():
    try:
        name = request.form.get('name')
        telephone = request.form.get('telephone')
        email = request.form.get('email', '')
        age = request.form.get('age', '')
        vacancy_type = request.form.get('vacancy_type')
        experience = request.form.get('experience', '')
        education = request.form.get('education', '')
        driving_license = request.form.get('driving_license', '')
        message = request.form.get('message', '')
        
        # Проверка согласия на обработку данных
        if not request.form.get('consent'):
            return render_template('work/work_order.html', error="Необходимо дать согласие на обработку персональных данных", latest_news=g.latest_news)
        
        # Обработка загруженного файла резюме
        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Добавляем временную метку к имени файла, чтобы избежать конфликтов
                resume_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
        
        # Сохранение в базу данных
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO work_applications (name, telephone, email, age, vacancy_type, experience, 
            education, driving_license, message, resume_file, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (name, telephone, email, age, vacancy_type, experience, education, 
              driving_license, message, resume_filename, 'Новая'))
        conn.commit()
        conn.close()
        
        return render_template('work/work_order.html', success="Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.", latest_news=g.latest_news)
    except Exception as e:
        print(f"Error in submit_work_order: {e}")
        return render_template('work/work_order.html', error="Произошла ошибка при отправке заявки. Пожалуйста, попробуйте еще раз позже.", latest_news=g.latest_news)

# === Обработка ошибок ===
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error/500.html'), 500

@app.route('/your-ticket')
def your_ticket():
    return render_template('your-ticket.html', latest_news=g.latest_news)

@app.route('/about-company')
def about_company():
    return render_template('about-us/about-company.html', latest_news=g.latest_news)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # Используем PORT от Render, по умолчанию 5000
    app.run(host='0.0.0.0', port=port)