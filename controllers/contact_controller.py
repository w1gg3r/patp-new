from flask import Blueprint, request, redirect, url_for, flash
from config.database import get_db_connection

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    telephone = request.form.get('telephone')
    subject = request.form.get('subject', '')
    message = request.form.get('message')
    consent = request.form.get('consent')

    if not name or not email or not telephone or not message or not consent:
        flash('error', 'Все обязательные поля должны быть заполнены.')
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO feedback (name, email, telephone, subject, message, consent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, telephone, subject, message, True))
        conn.commit()
        conn.close()

        flash('Заявка успешно отправлена!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        conn.rollback()
        conn.close()
        flash('error', f'Ошибка при отправке заявки: {str(e)}')
        return redirect(url_for('index'))