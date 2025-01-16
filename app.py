from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, login_required, current_user
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from db import db
from db.models import users8
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))  # Генерация секретного ключа
CORS(app, supports_credentials=True)

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

login_manager.init_app(app)

app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(lab8)
app.register_blueprint(rgz)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'rgz.login'  # Укажи правильный маршрут для авторизации
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return users8.query.get(int(user_id))

# Конфигурация приложения
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json; charset=utf-8"

if app.config['DB_TYPE'] == 'postgres':
    db_name = 'chuvashova_rita_orm'
    db_user = 'chuvashova_rita_orm'
    db_password = '4321'
    host_ip = '127.0.0.1'
    host_port = 5432

    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'postgresql://{db_user}:{db_password}@{host_ip}:{host_port}/{db_name}'

else:
    dir_path = path.dirname(path.realpath(__file__))
    db_path = path.join(dir_path, "oparina_sofya_orm.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)

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
