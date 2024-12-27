from flask import Flask, redirect, url_for, render_template
import os
import secrets
from flask_cors import CORS

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
from rgz import rgz

app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(rgz)

# Конфигурация приложения
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json; charset=utf-8"

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
