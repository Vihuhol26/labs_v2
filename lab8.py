from flask import Blueprint, render_template, request, redirect, session, abort
from db import db
from db.models import users8, articles
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user 

lab8 = Blueprint('lab8', __name__)


@lab8.route('/lab8/')
def lab():
    return render_template('lab8/lab8.html', login = current_user.login if current_user.is_authenticated else None )

@lab8.route('/lab8/register/', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')

    login_exists = users8.query.filter_by(login = login_form).first()
    if login_exists:
        return render_template('lab8/register.html', error = 'Такой пользователь уже существует')
    
    if not login_form or not password_form:
        return render_template('lab8/register.html', error='Заполните все поля')
    
    password_hash = generate_password_hash(password_form)
    new_user = users8(login = login_form, password = password_hash)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/lab8')

@lab8.route('/lab8/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('remember')

    user = users8.query.filter_by(login = login_form).first()

    if not login_form or not password_form:
        return render_template('lab8/login.html', error='Заполните все поля')

    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=bool(remember))
            return redirect('/lab8/')    
        
    return render_template('/lab8/login.html', 
                           error = 'Ошибка входа: логин и/или пароль неверны')


@lab8.route('/lab8/articles/', methods = ['GET', 'POST'])
@login_required
def article_list():
    user_articles = articles.query.filter_by(login_id=current_user.id).all()
    return render_template('lab8/articles.html', articles=user_articles)

@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8')

@lab8.route('/lab8/create/', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_favorite = bool(request.form.get('is_favorite'))
    is_public = bool(request.form.get('is_public'))

    if not title or not article_text:
        return render_template('lab8/create.html', error='Заполните все поля')

    # Создание новой статьи
    new_article = articles(
        title=title,
        article_text=article_text,
        is_favorite=is_favorite,
        is_public=is_public,
        likes=0,  
        login_id=current_user.id  
    )
    db.session.add(new_article)
    db.session.commit()

    return redirect('/lab8/articles/')

@lab8.route('/lab8/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.filter_by(id=article_id).first()

    # Проверка, что текущий пользователь — автор статьи
    if article.login_id != current_user.id:
        return redirect('/lab8/articles')  # Перенаправляем, если пользователь не автор

    if request.method == 'GET':
        return render_template('lab8/edit_article.html', article=article)

    # Обработка POST-запроса
    title_form = request.form.get('title')
    text_form = request.form.get('article_text')

    if not title_form or not text_form:
        return render_template('lab8/edit_article.html', article=article, error='Заполните все поля')

    # Обновление статьи
    article.title = title_form
    article.article_text = text_form
    db.session.commit()

    return redirect('/lab8/articles/')

@lab8.route('/lab8/articles/delete/<int:article_id>')
@login_required
def delete_article(article_id):
    article = articles.query.filter_by(id = article_id).first()
    if not article:
        abort(404)
    if article.login_id != current_user.id:
         abort(403)
    db.session.delete(article)
    db.session.commit()
    return redirect('/lab8/articles/')