from flask import Blueprint, request, redirect, url_for, Response, render_template, jsonify
from functools import wraps
import pymysql
from pymysql.cursors import DictCursor
import json
from decimal import Decimal
import requests
import os
import logging
from flask_login import login_user, logout_user, login_required, current_user, UserMixin, LoginManager
from tenacity import retry, stop_after_attempt, wait_fixed
from sqlalchemy.exc import OperationalError

# Создаем Blueprint
rgz = Blueprint('rgz', __name__)

# Инициализация LoginManager
login_manager = LoginManager()
login_manager.login_view = 'rgz.login'  # Указываем страницу для авторизации

# Класс пользователя
class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict['id']
        self.username = user_dict['username']
        self.user_type = user_dict['user_type']
        self.balance = user_dict.get('balance', 0)
        self.phone = user_dict.get('phone', '')
        self.account_number = user_dict.get('account_number', '')

# Загрузчик пользователя
@login_manager.user_loader
def load_user(user_id):
    try:
        conn, cur = db_connect()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_dict = cur.fetchone()
        db_close(conn, cur)

        if user_dict:
            return User(user_dict)
        return None
    except Exception as e:
        logging.error(f"Ошибка при загрузке пользователя: {e}")
        return None

# Кастомный сериализатор для Decimal
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Преобразуем Decimal в float
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Подключение к базе данных MySQL с ретри-логикой
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def db_connect():
    try:
        conn = pymysql.connect(
            host='Vihuhol.mysql.pythonanywhere-services.com',  # Хост
            user='Vihuhol',  # Пользователь
            password='Qwerty220140',  # Пароль
            database='Vihuhol$default',  # Имя базы данных
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        cur = conn.cursor()
        logging.debug("Подключение к базе данных успешно установлено!")
        return conn, cur
    except pymysql.Error as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        raise OperationalError("Ошибка подключения к базе данных", e)

# Закрытие соединения с базой данных
def db_close(conn, cur):
    try:
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"Ошибка при закрытии соединения: {e}")

# Декоратор для проверки прав менеджера
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'manager':
            return jsonify({"error": "Доступ запрещен"}), 403
        return f(*args, **kwargs)
    return decorated_function

@rgz.route('/jsonrpc', methods=['POST'])
def jsonrpc():
    data = request.get_json()
    if data['method'] == 'get_transaction_history':
        user_id = data['params']['user_id']
        try:
            conn, cur = db_connect()
            cur.execute("SELECT * FROM transactions WHERE sender_id = %s OR receiver_id = %s", (user_id, user_id))
            transactions = cur.fetchall()
            db_close(conn, cur)

            return jsonify({
                "jsonrpc": "2.0",
                "result": {"transactions": transactions},
                "id": data['id']
            })
        except Exception as e:
            logging.error(f"Ошибка при получении истории транзакций: {e}")
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error"},
                "id": data['id']
            }), 500
    else:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": data['id']
        }), 404

@rgz.route('/rgz/dashboard')
@login_required
def dashboard():
    try:
        user_id = current_user.id
        conn, cur = db_connect()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        db_close(conn, cur)

        if not user:
            return "Пользователь не найден", 404

        return render_template('rgz/dashboard.html', user=user)
    except OperationalError as e:
        logging.error(f"Ошибка базы данных: {e}")
        return "Ошибка базы данных", 500
    except BrokenPipeError:
        logging.error("Клиент закрыл соединение")
        return "Клиент закрыл соединение", 400

@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            conn, cur = db_connect()
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            user_dict = cur.fetchone()
            db_close(conn, cur)

            if user_dict is None:
                return jsonify({"error": "Пользователь не найден"}), 404

            if user_dict['password'] == password:
                user = User(user_dict)
                login_user(user)
                return jsonify({"message": "Авторизация успешна", "redirect": url_for('rgz.dashboard')}), 200
            return jsonify({"error": "Неверный пароль"}), 401
        except Exception as e:
            logging.error(f"Ошибка при выполнении запроса: {e}")
            return jsonify({"error": "Ошибка сервера"}), 500

    elif request.method == 'GET':
        return render_template('rgz/login.html')

@rgz.route('/rgz/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'GET':
        return render_template('rgz/transfer.html')

    data = request.get_json()
    if not data:
        return jsonify({"error": "Отсутствуют данные в запросе"}), 400

    sender_id = current_user.id
    receiver_phone = data.get('receiver_phone')
    amount = data.get('amount')

    if not receiver_phone or not amount:
        return jsonify({"error": "Все поля обязательны"}), 400

    if amount <= 0:
        return jsonify({"error": "Сумма перевода должна быть больше нуля"}), 400

    conn, cur = db_connect()
    try:
        cur.execute("SELECT id FROM users WHERE phone = %s", (receiver_phone,))
        receiver = cur.fetchone()
        if not receiver:
            return jsonify({"error": "Получатель не найден"}), 404

        receiver_id = receiver['id']

        cur.execute("SELECT balance FROM users WHERE id = %s", (sender_id,))
        sender_balance = cur.fetchone()['balance']
        if sender_balance < amount:
            return jsonify({"error": "Недостаточно средств"}), 400

        cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, sender_id))
        cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, receiver_id))

        cur.execute(
            "INSERT INTO transactions (sender_id, receiver_id, amount) VALUES (%s, %s, %s)",
            (sender_id, receiver_id, amount)
        )

        conn.commit()
        return jsonify({"message": "Перевод успешно выполнен"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Ошибка при переводе средств: {str(e)}"}), 500
    finally:
        db_close(conn, cur)

@rgz.route('/rgz/create_user', methods=['GET', 'POST'])
@manager_required
def create_user():
    if request.method == 'GET':
        return render_template('rgz/create_user.html')
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Запрос должен быть в формате JSON"}), 415

        data = request.get_json()
        full_name = data.get('full_name')
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        account_number = data.get('account_number')
        balance = data.get('balance', 1000)
        user_type = data.get('user_type', 'user')

        if not all([full_name, username, password]):
            return jsonify({"error": "Не все обязательные поля заполнены"}), 400

        conn, cur = db_connect()
        try:
            cur.execute(
                "INSERT INTO users (full_name, username, password, phone, account_number, balance, user_type) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (full_name, username, password, phone, account_number, balance, user_type)
            )
            user_id = cur.lastrowid
            conn.commit()
            return jsonify({"id": user_id}), 201
        except pymysql.Error as e:
            conn.rollback()
            return jsonify({"error": f"Ошибка при создании пользователя: {str(e)}"}), 500
        finally:
            db_close(conn, cur)

@rgz.route('/rgz/transaction_history')
@login_required
def transaction_history():
    try:
        user_id = current_user.id
        conn, cur = db_connect()
        cur.execute("SELECT * FROM transactions WHERE sender_id = %s OR receiver_id = %s", (user_id, user_id))
        transactions = cur.fetchall()
        db_close(conn, cur)

        return render_template('rgz/transaction_history.html', transactions=transactions)
    except Exception as e:
        logging.error(f"Ошибка при получении истории транзакций: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500

@rgz.route('/rgz/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Вы успешно вышли из системы", "redirect": url_for('rgz.login')}), 200

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)