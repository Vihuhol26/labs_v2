from flask import Blueprint, request, session, redirect, url_for, Response, render_template
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from decimal import Decimal
import requests
import os
import logging

# Создаем Blueprint
rgz = Blueprint('rgz', __name__)

# Кастомный сериализатор для Decimal
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Преобразуем Decimal в float
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Подключение к базе данных
def db_connect():
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='knowledge_base',
            user='knowledge_base',
            password='123',
            client_encoding='UTF8'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        print("Подключение к базе данных успешно установлено!")  # Отладочное сообщение
        return conn, cur
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")  # Отладочное сообщение
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
        print("Текущий user_type в декораторе:", session.get('user_type'))  # Отладочный вывод
        if 'user_id' not in session or session.get('user_type') != 'manager':
            return json.dumps({"error": "Доступ запрещен"}), 403, {'Content-Type': 'application/json'}
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
        return Response(
            json.dumps({
                "jsonrpc": "2.0",
                "result": {"transactions": transactions},
                "id": data['id']
            }),
            mimetype='application/json'
        )
    else:
        return Response(
            json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": data['id']
            }),
            mimetype='application/json',
            status=404
        )

@rgz.route('/rgz/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('rgz.login'))

    user_id = session['user_id']
    conn, cur = db_connect()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    db_close(conn, cur)

    if not user:
        return "Пользователь не найден", 404

    return render_template('rgz/dashboard.html', user=user)

# Авторизация пользователя
@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('rgz/login.html')
    elif request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        conn, cur = db_connect()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        db_close(conn, cur)

        if user is None:
            return json.dumps({"error": "Пользователь не найден"}), 404, {'Content-Type': 'application/json'}

        if user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = username
            session['user_type'] = user['user_type']  # Сохраняем тип пользователя
            print("Данные сессии после авторизации:", session)  # Отладочный вывод
            return json.dumps({"message": "Авторизация успешна", "redirect": url_for('rgz.dashboard')}), 200, {'Content-Type': 'application/json'}
        return json.dumps({"error": "Неверный пароль"}), 401, {'Content-Type': 'application/json'}

@rgz.route('/rgz/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:  # Проверка авторизации на сервере
        return redirect(url_for('rgz.login'))

    if request.method == 'GET':
        return render_template('rgz/transfer.html')

    # Логика для POST-запроса
    data = request.get_json()
    if not data:
        response_data = json.dumps({"error": "Отсутствуют данные в запросе"})
        return Response(response_data, status=400, mimetype='application/json')

    sender_id = session['user_id']
    receiver_phone = data.get('receiver_phone')
    amount = data.get('amount')

    if not receiver_phone or not amount:
        response_data = json.dumps({"error": "Все поля обязательны"})
        return Response(response_data, status=400, mimetype='application/json')

    if amount <= 0:
        response_data = json.dumps({"error": "Сумма перевода должна быть больше нуля"})
        return Response(response_data, status=400, mimetype='application/json')

    conn, cur = db_connect()
    try:
        cur.execute("SELECT id FROM users WHERE phone = %s", (receiver_phone,))
        receiver = cur.fetchone()
        if not receiver:
            response_data = json.dumps({"error": "Получатель не найден"})
            return Response(response_data, status=404, mimetype='application/json')

        cur.execute("SELECT balance FROM users WHERE id = %s", (sender_id,))
        sender_balance = cur.fetchone()['balance']
        if sender_balance < amount:
            response_data = json.dumps({"error": "Недостаточно средств"})
            return Response(response_data, status=400, mimetype='application/json')

        cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, sender_id))
        cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, receiver['id']))
        conn.commit()

        response_data = json.dumps({"message": "Перевод успешно выполнен"})
        return Response(response_data, status=200, mimetype='application/json')
    except Exception as e:
        conn.rollback()
        response_data = json.dumps({"error": f"Ошибка при переводе средств: {str(e)}"})
        return Response(response_data, status=500, mimetype='application/json')
    finally:
        db_close(conn, cur)
        
@rgz.route('/rgz/create_user', methods=['GET', 'POST'])
@manager_required
def create_user():
    if request.method == 'GET':
        return render_template('rgz/create_user.html')
    elif request.method == 'POST':
        if not request.is_json:
            return json.dumps({"error": "Запрос должен быть в формате JSON"}), 415, {'Content-Type': 'application/json'}

        data = request.get_json()
        print("Данные для создания пользователя:", data)  # Отладочный вывод

        full_name = data.get('full_name')
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        account_number = data.get('account_number')
        balance = data.get('balance', 1000)
        user_type = data.get('user_type', 'user')

        if not all([full_name, username, password]):
            return json.dumps({"error": "Не все обязательные поля заполнены"}), 400, {'Content-Type': 'application/json'}

        conn, cur = db_connect()
        try:
            cur.execute(
                "INSERT INTO users (full_name, username, password, phone, account_number, balance, user_type) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (full_name, username, password, phone, account_number, balance, user_type)
            )
            user_id = cur.fetchone()['id']
            conn.commit()
            return json.dumps({"id": user_id}), 201, {'Content-Type': 'application/json'}
        except psycopg2.Error as e:
            conn.rollback()
            return json.dumps({"error": f"Ошибка при создании пользователя: {str(e)}"}), 500, {'Content-Type': 'application/json'}
        finally:
            db_close(conn, cur)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

@rgz.route('/rgz/transaction_history')
def transaction_history():
    # Проверка авторизации пользователя
    if 'user_id' not in session:
        logging.warning("Пользователь не авторизован")
        return redirect(url_for('rgz.login'))

    user_id = session['user_id']
    logging.debug(f"Запрос истории транзакций для пользователя: {user_id}")

    try:
        # Вызов JSON-RPC метода get_transaction_history
        response = requests.post(
            'http://127.0.0.1:5000/jsonrpc',
            json={
                "jsonrpc": "2.0",
                "method": "get_transaction_history",
                "params": {"user_id": user_id},
                "id": 1
            }
        )

        # Логирование ответа
        logging.debug(f"Статус ответа: {response.status_code}")
        logging.debug(f"Содержимое ответа: {response.text}")

        # Проверка статуса ответа
        if response.status_code != 200:
            logging.error(f"Ошибка сервера: {response.status_code}")
            return Response(
                json.dumps({"error": "Ошибка сервера"}),
                status=500,
                mimetype='application/json'
            )

        # Проверка содержимого ответа
        if not response.text:
            logging.error("Пустой ответ от сервера")
            return Response(
                json.dumps({"error": "Пустой ответ от сервера"}),
                status=500,
                mimetype='application/json'
            )

        # Декодирование JSON
        try:
            data = response.json()
        except ValueError as e:
            logging.error(f"Ошибка при декодировании JSON: {str(e)}")
            return Response(
                json.dumps({"error": f"Ошибка при декодировании JSON: {str(e)}"}),
                status=500,
                mimetype='application/json'
            )

        # Проверка наличия ошибки в ответе
        if 'error' in data:
            logging.error(f"Ошибка JSON-RPC: {data['error']}")
            return Response(
                json.dumps(data['error']),
                status=400,
                mimetype='application/json'
            )

        # Получение транзакций
        transactions = data['result']['transactions']
        logging.debug(f"Получено транзакций: {len(transactions)}")
        return render_template('rgz/transaction_history.html', transactions=transactions)

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса: {str(e)}")
        return Response(
            json.dumps({"error": f"Ошибка при выполнении запроса: {str(e)}"}),
            status=500,
            mimetype='application/json'
        )
# Выход из системы
@rgz.route('/rgz/logout', methods=['POST'])
def logout():
    session.clear()
    return json.dumps({"message": "Вы успешно вышли из системы", "redirect": url_for('rgz.login')}), 200, {'Content-Type': 'application/json'}

@rgz.route('/rgz/manage_users')
@manager_required
def manage_users():
    return render_template('rgz/manage_users.html')

# Редактирование пользователя (только для менеджеров)
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
        return json.dumps({"message": "Пользователь успешно обновлен"}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": f"Ошибка при обновлении пользователя: {str(e)}"}), 500, {'Content-Type': 'application/json'}
    finally:
        db_close(conn, cur)

@rgz.route('/rgz/users/<int:user_id>', methods=['DELETE'])
@manager_required
def delete_user(user_id):
    conn, cur = db_connect()
    try:
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        return json.dumps({"message": "Пользователь успешно удален"}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": f"Ошибка при удалении пользователя: {str(e)}"}), 500, {'Content-Type': 'application/json'}
    finally:
        db_close(conn, cur)
        
@rgz.route('/rgz/users', methods=['GET', 'POST'])  # Добавлен метод POST
@manager_required
def users():
    if request.method == 'GET':
        # Обработка GET-запроса (получение списка пользователей)
        conn, cur = db_connect()
        try:
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
            return json.dumps({"users": users}, default=decimal_default), 200, {'Content-Type': 'application/json'}
        except Exception as e:
            return json.dumps({"error": f"Ошибка при получении списка пользователей: {str(e)}"}), 500, {'Content-Type': 'application/json'}
        finally:
            db_close(conn, cur)

    elif request.method == 'POST':
        # Обработка POST-запроса (создание пользователя)
        if not request.is_json:
            return json.dumps({"error": "Запрос должен быть в формате JSON"}), 415, {'Content-Type': 'application/json'}

        data = request.get_json()
        full_name = data.get('full_name')
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        account_number = data.get('account_number')
        balance = data.get('balance', 1000)
        user_type = data.get('user_type', 'user')

        if not all([full_name, username, password]):
            return json.dumps({"error": "Не все обязательные поля заполнены"}), 400, {'Content-Type': 'application/json'}

        conn, cur = db_connect()
        try:
            cur.execute(
                "INSERT INTO users (full_name, username, password, phone, account_number, balance, user_type) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (full_name, username, password, phone, account_number, balance, user_type)
            )
            user_id = cur.fetchone()['id']
            conn.commit()
            return json.dumps({"id": user_id}), 201, {'Content-Type': 'application/json'}
        except psycopg2.Error as e:
            conn.rollback()
            return json.dumps({"error": f"Ошибка при создании пользователя: {str(e)}"}), 500, {'Content-Type': 'application/json'}
        finally:
            db_close(conn, cur)