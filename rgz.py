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
        self.is_active = True  # Убедитесь, что этот атрибут есть

# Загрузчик пользователя
@login_manager.user_loader
def load_user(user_id):
    conn, cur = db_connect()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_dict = cur.fetchone()
    db_close(conn, cur)

    if user_dict:
        return User(user_dict)
    return None

# Кастомный сериализатор для Decimal
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Преобразуем Decimal в float
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Подключение к базе данных MySQL
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
        return None, None

# Закрытие соединения с базой данных
def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

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
        # Логика для получения истории транзакций
        transactions = [
            {"id": 1, "amount": 100, "date": "2024-01-01"},
            {"id": 2, "amount": 200, "date": "2024-01-02"}
        ]
        return jsonify({
            "jsonrpc": "2.0",
            "result": {"transactions": transactions},
            "id": data['id']
        })
    else:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": data['id']
        }), 404

@rgz.route('/rgz/dashboard')
@login_required
def dashboard():
    user_id = current_user.id  # Используем current_user
    conn, cur = db_connect()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    db_close(conn, cur)

    if not user:
        return "Пользователь не найден", 404

    return render_template('rgz/dashboard.html', user=user)

# Авторизация пользователя
@rgz.route('/rgz/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        conn, cur = db_connect()
        if cur is None:
            return jsonify({"error": "Ошибка подключения к базе данных"}), 500

        try:
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            user_dict = cur.fetchone()
            db_close(conn, cur)

            if user_dict is None:
                return jsonify({"error": "Пользователь не найден"}), 404

            if user_dict['password'] == password:
                user = User(user_dict)  # Создаем объект User
                login_user(user)  # Авторизуем пользователя
                return jsonify({"message": "Авторизация успешна", "redirect": url_for('rgz.dashboard')}), 200
            return jsonify({"error": "Неверный пароль"}), 401
        except Exception as e:
            logging.error(f"Ошибка при выполнении запроса: {e}")
            return jsonify({"error": "Ошибка сервера"}), 500

@rgz.route('/rgz/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'GET':
        return render_template('rgz/transfer.html')

    # Логика для POST-запроса
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
        # Находим получателя по номеру телефона
        cur.execute("SELECT id FROM users WHERE phone = %s", (receiver_phone,))
        receiver = cur.fetchone()
        if not receiver:
            return jsonify({"error": "Получатель не найден"}), 404

        receiver_id = receiver['id']

        # Проверяем баланс отправителя
        cur.execute("SELECT balance FROM users WHERE id = %s", (sender_id,))
        sender_balance = cur.fetchone()['balance']
        if sender_balance < amount:
            return jsonify({"error": "Недостаточно средств"}), 400

        # Обновляем балансы
        cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, sender_id))
        cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, receiver_id))

        # Сохраняем транзакцию
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
            user_id = cur.lastrowid  # Получаем ID последней вставленной записи
            conn.commit()
            return jsonify({"id": user_id}), 201
        except pymysql.Error as e:
            conn.rollback()
            return jsonify({"error": f"Ошибка при создании пользователя: {str(e)}"}), 500
        finally:
            db_close(conn, cur)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

@rgz.route('/rgz/transaction_history')
@login_required
def transaction_history():
    user_id = current_user.id
    logging.debug(f"Запрос истории транзакций для пользователя: {user_id}")

    try:
        response = requests.post(
            'http://vihuhol.pythonanywhere.com/jsonrpc',
            json={
                "jsonrpc": "2.0",
                "method": "get_transaction_history",
                "params": {"user_id": user_id},
                "id": 1
            }
        )

        if response.status_code != 200:
            logging.error(f"Ошибка сервера: {response.status_code}")
            return jsonify({"error": "Ошибка сервера"}), 500

        data = response.json()
        if 'error' in data:
            logging.error(f"Ошибка JSON-RPC: {data['error']}")
            return jsonify(data['error']), 400

        transactions = data['result']['transactions']
        logging.debug(f"Получено транзакций: {len(transactions)}")
        return render_template('rgz/transaction_history.html', transactions=transactions)

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса: {str(e)}")
        return jsonify({"error": f"Ошибка при выполнении запроса: {str(e)}"}), 500

@rgz.route('/rgz/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Вы успешно вышли из системы", "redirect": url_for('rgz.login')}), 200

@rgz.route('/rgz/manage_users')
@manager_required
def manage_users():
    return render_template('rgz/manage_users.html')

@rgz.route('/rgz/users/<int:user_id>', methods=['PUT'])
@manager_required
def update_user(user_id):
    data = request.get_json()
    full_name = data.get('full_name')
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')
    account_number = data.get('account_number')
    balance = data.get('balance')
    user_type = data.get('user_type')

    conn, cur = db_connect()
    try:
        cur.execute("UPDATE users SET full_name=%s, username=%s, password=%s, phone=%s, account_number=%s, balance=%s, user_type=%s WHERE id=%s",
                    (full_name, username, password, phone, account_number, balance, user_type, user_id))
        conn.commit()
        return jsonify({"message": "Пользователь успешно обновлен"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Ошибка при обновлении пользователя: {str(e)}"}), 500
    finally:
        db_close(conn, cur)

@rgz.route('/rgz/users/<int:user_id>', methods=['DELETE'])
@manager_required
def delete_user(user_id):
    conn, cur = db_connect()
    try:
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        return jsonify({"message": "Пользователь успешно удален"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Ошибка при удалении пользователя: {str(e)}"}), 500
    finally:
        db_close(conn, cur)

@rgz.route('/rgz/users', methods=['GET', 'POST'])
@manager_required
def users():
    if request.method == 'GET':
        conn, cur = db_connect()
        try:
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
            return jsonify({"users": users}), 200
        except Exception as e:
            return jsonify({"error": f"Ошибка при получении списка пользователей: {str(e)}"}), 500
        finally:
            db_close(conn, cur)

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
            