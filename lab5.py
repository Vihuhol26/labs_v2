from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

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
        dir_path = path.dirname(path.abspath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        conn.row_factory = sqlite3.Row

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

    cur.execute("SELECT login FROM users WHERE login=%s;", (login,))
    existing_user = cur.fetchone()

    if existing_user:
        db_close(conn, cur)
        return render_template('lab5/register.html', error="Такой пользователь уже существует")

    password_hash = generate_password_hash(password)

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, password_hash))
    else:
        cur.execute("INSERT INTO users (login, password) VALUES (?, ?);", (login, password_hash))

    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)

@lab5.route('/lab5/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not (login and password):
        return render_template('lab5/login.html', error="Заполните поле")

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login,))
    user = cur.fetchone()

    if not user or not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html', error='Логин и/или пароль неверны')

    session['login'] = login
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login)

@lab5.route('/lab5/create', methods=['GET', 'POST'])
def create():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    if request.method == 'GET':
        return render_template('lab5/create_articles.html')

    title = request.form.get('title')
    article_text = request.form.get('article_text')

    if not title or not article_text:
        return render_template('lab5/create_articles.html', error="Тема и текст статьи не могут быть пустыми")

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
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
def list_articles():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
    users = cur.fetchone()
    user_id = users["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE user_id = %s;", (user_id,))
    else:
        cur.execute("SELECT * FROM articles WHERE user_id = ?;", (user_id,))
    articles = cur.fetchall()

    db_close(conn, cur)

    if not articles:
        return render_template('lab5/articles.html', articles=articles, message="У вас нет ни одной статьи.")

    return render_template('lab5/articles.html', articles=articles)

@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    return render_template('lab5/login.html')  
@lab5.route('/lab5/edit', methods=['GET', 'POST'])
def edit():
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
        cur.execute("SELECT * FROM articles WHERE user_id = %s;", (user_id,))
    else:
        cur.execute("SELECT * FROM articles WHERE user_id = ?;", (user_id,))
    
    articles = cur.fetchall()
    if request.method == 'POST':
        title = request.form.get('title')
        article_text = request.form.get('article_text')
        article_id = request.form.get('id')
   
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE articles SET title = %s, article_text = %s WHERE id = %s AND user_id = %s;", 
                        (title, article_text, article_id, user_id))
        else:
            cur.execute("UPDATE articles SET title = ?, article_text = ? WHERE id = ? AND user_id = ?;", 
                        (title, article_text, article_id, user_id))
        db_close(conn, cur)
        return redirect('/lab5/list')  
    db_close(conn, cur)
    return render_template('lab5/edit_article.html', articles=articles)
@lab5.route('/lab5/delete', methods=['POST'])
def delete():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
    
    user = cur.fetchone() 
    if not user:
        return redirect('/lab5/login')
    article_id = request.form.get('id')
    if not article_id:
        return "Article ID missing", 400  
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM articles WHERE id = %s AND user_id = %s;", (article_id, user["id"]))
    else:
        cur.execute("DELETE FROM articles WHERE id = ? AND user_id = ?;", (article_id, user["id"]))
    db_close(conn, cur)
    return redirect('/lab5/list')
