from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import secrets
from os import path

# Создаем приложение Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))  # Генерация секретного ключа
CORS(app, supports_credentials=True)

# Настройка подключения к MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://Vihuhol:Qwerty220140@Vihuhol.mysql.pythonanywhere-services.com/Vihuhol$default'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем предупреждения

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    user_type = db.Column(db.String(20), default='user')

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'rgz.login'  # Указываем страницу для авторизации
login_manager.init_app(app)

# Загрузчик пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Импорт и регистрация Blueprints
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
from lab5 import lab5
from lab6 import lab6
from lab7 import lab7
from lab8 import lab8
from rgz import rgz

app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(lab8)
app.register_blueprint(rgz)

# Создание таблиц в базе данных (если их нет)
with app.app_context():
    db.create_all()

# Маршруты
@app.route("/")
@app.route("/index")
def start():
    return redirect(url_for('menu'), code=302)

@app.route("/menu")
def menu():
    return render_template('menu.html')

@app.route("/rgz")
def menu_rgz():
    return render_template('rgz.html')
