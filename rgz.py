from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
import os

rgz = Blueprint('rgz', __name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'секретный-секрет'

def db_connect():
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='knowledge_base',
        user='knowledge_base',
        password='123',
        client_encoding='UTF8'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['user_type'] != 'manager':
            return redirect(url_for('rgz.login'))
        return f(*args, **kwargs)
    return decorated_function

# Главная страница
@rgz.route('/rgz/')
def lab():
    user_id = session.get('user_id')
    if user_id:
        conn, cur = db_connect()
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        db_close(conn, cur)
    else:
        user = None

    return render_template('rgz/rgz.html', login=session.get('login'), user=user)

# Страница входа
@rgz.route('/rgz/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn, cur = db_connect()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        db_close(conn, cur)

        if user is None:
            return render_template('rgz/login.html', error="Такого пользователя не существует")

        if user['password'] == password:
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            return redirect(url_for('rgz.dashboard'))
        else:
            return render_template('rgz/login.html', error="Неверный пароль")

    return render_template('rgz/login.html')

# Страница панели управления
@rgz.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('rgz.login'))

    user_id = session['user_id']
    conn, cur = db_connect()
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    db_close(conn, cur)

    return render_template('rgz/dashboard.html', user=user)

# Перевод средств
@rgz.route('/transfer', methods=['POST'])
def transfer():
    sender_id = session['user_id']
    receiver_id = request.form['receiver_id']
    amount = float(request.form['amount'])

    if not receiver_id.isdigit():
        return "Ошибка: ID получателя должен быть числом"

    receiver_id = int(receiver_id)

    if amount <= 0:
        return "Ошибка: Сумма перевода должна быть больше нуля"

    conn, cur = db_connect()
    try:
        cur.execute("SELECT balance FROM users WHERE id=%s", (sender_id,))
        balance = cur.fetchone()['balance']

        if balance < amount:
            return "Недостаточно средств на счете"

        cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, sender_id))
        cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, receiver_id))
        cur.execute("INSERT INTO transactions (sender_id, receiver_id, amount) VALUES (%s, %s, %s)",
                    (sender_id, receiver_id, amount))

        conn.commit()
        return redirect(url_for('rgz.transfer_success'))

    except Exception as e:
        conn.rollback()
        return f"Ошибка при выполнении транзакции: {str(e)}"
    finally:
        db_close(conn, cur)

# Страница успешного перевода
@rgz.route('/transfer_success')
def transfer_success():
    return render_template('rgz/transfer_success.html')

# Выбор пользователя для редактирования
@rgz.route('/select_user', methods=['GET'])
@manager_required
def select_user():
    conn, cur = db_connect()
    cur.execute("SELECT id, full_name FROM users")
    users = cur.fetchall()
    db_close(conn, cur)

    user_id = request.args.get('user_id')
    if user_id:
        return redirect(url_for('rgz.edit_user', user_id=user_id))

    return render_template('rgz/select_user.html', users=users)

# Редактирование пользователя
@rgz.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@manager_required
def edit_user(user_id):
    if user_id == session['user_id']:
        return "Вы не можете редактировать сами себя"

    conn, cur = db_connect()

    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        account_number = request.form['account_number']
        balance = float(request.form['balance'])
        user_type = request.form['user_type']

        cur.execute("""
            UPDATE users SET
            full_name=%s, username=%s, password=%s, phone=%s, account_number=%s, balance=%s, user_type=%s
            WHERE id=%s
        """, (full_name, username, password, phone, account_number, balance, user_type, user_id))

        conn.commit()
        db_close(conn, cur)

        return redirect(url_for('rgz.select_user'))

    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    db_close(conn, cur)

    return render_template('rgz/edit_user.html', user=user)

# Удаление пользователя
@rgz.route('/delete_user/<int:user_id>', methods=['POST'])
@manager_required
def delete_user(user_id):
    if user_id == session['user_id']:
        return "Вы не можете удалить сами себя"

    conn, cur = db_connect()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    db_close(conn, cur)

    return redirect(url_for('rgz.select_user'))

# Создание пользователя
@rgz.route('/create_user', methods=['GET', 'POST'])
@manager_required
def create_user():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        account_number = request.form['account_number']
        balance = 1000
        user_type = request.form['user_type']

        conn, cur = db_connect()
        cur.execute("INSERT INTO users (full_name, username, password, phone, account_number, balance, user_type) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (full_name, username, password, phone, account_number, balance, user_type))
        conn.commit()
        db_close(conn, cur)

        return redirect(url_for('rgz.select_user'))

    return render_template('rgz/create_user.html')

# История транзакций
@rgz.route('/transaction_history')
def transaction_history():
    if 'user_id' not in session:
        return redirect(url_for('rgz.login'))

    user_id = session['user_id']
    conn, cur = db_connect()
    cur.execute("SELECT * FROM transactions WHERE sender_id=%s OR receiver_id=%s", (user_id, user_id))
    transactions = cur.fetchall()
    db_close(conn, cur)

    return render_template('rgz/transaction_history.html', transactions=transactions)

# Получение списка пользователей (JSON)
@rgz.route('/users', methods=['GET'])
def users():
    conn, cur = db_connect()
    cur.execute("SELECT id, full_name FROM users")
    users = cur.fetchall()
    db_close(conn, cur)
    return jsonify(users)

# Выход из системы
@rgz.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('rgz.login'))
