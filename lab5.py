from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash

lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login=session.get('login'))

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='chuvashova_rita_knowledge_base',
            user='chuvashova_rita_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab5.route('/lab5/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not (login and password):
        return render_template('lab5/register.html', error="Заполните все поля")

    conn, cur = db_connect()

    cur.execute(f"SELECT login FROM users WHERE login='{login}';")
    existing_user = cur.fetchone()

    if existing_user:
        db_close(conn, cur)
        return render_template('lab5/register.html', error="Такой пользователь уже существует")

    password_hash = generate_password_hash(password)

    cur.execute(f"INSERT INTO users (login, password) VALUES ('{login}', '{password_hash}');")

    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)

@lab5.route('/lab5/create')
def create_article():
    return render_template('lab5/create.html', username='anonymous')

@lab5.route('/lab5/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not (login or password):
        return render_template('lab5/login.html', error="Заполните поле")

    conn, cur = db_connect()

    cur.execute("SELECT login, password FROM users WHERE login=%s;", (login,))
    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html', error='Логин и/или пароль неверны')

    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html', error='Логин и/или пароль неверны')

    session['login'] = login
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login)

@lab5.route('/lab5/create_articles', methods=['GET', 'POST'])
def create():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    if request.method == 'GET':
        return render_template('lab5/create_articles.html')

    title = request.form.get('title')
    article_text = request.form.get('article_text')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;", (login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;", (login, ))
    users = cur.fetchone()
    user_id = users["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO articles (user_id, title, article_text) VALUES (%s, %s, %s);", 
                (user_id, title, article_text))
    else:
        cur.execute("INSERT INTO articles (user_id, title, article_text) VALUES (?, ?, ?);", 
                (user_id, title, article_text))

    db_close(conn, cur)
    return redirect('/lab5')

@lab5.route('/lab5/list', methods=['GET', 'POST'])
def list():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;", (login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;", (login, ))
    users = cur.fetchone()
    user_id = users["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE user_id = %s;", (user_id, ))
    else:
        cur.execute("SELECT * FROM articles WHERE user_id = ?;", (user_id, ))
    articles = cur.fetchall()

    db_close(conn, cur)
    return render_template('/lab5/articles.html', articles=articles)