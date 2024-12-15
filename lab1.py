from flask import Blueprint, url_for

lab1 = Blueprint('lab1', __name__)


@lab1.route("/menu")
def menu():
    return '''
<!doctype html>
<html>
    <head>
        <link rel="stylesheet" href="''' + url_for('static', filename='main.css') + '''">
        <title>НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных</title>
    </head>
    <body>
        <header>
            НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных
        </header>

        <main>
        <ol>
            <li><a href="http://127.0.0.1:5000/lab1">Первая лабораторная</a></li>
            <li><a href="http://127.0.0.1:5000/lab2">Вторая лабораторная</a></li>
            <li><a href="http://127.0.0.1:5000/lab3">Третья лабораторная</a></li>
            <li><a href="http://127.0.0.1:5000/lab4">Четвертая лабораторная</a></li>
            <li><a href="http://127.0.0.1:5000/lab5">Пятая лабораторная</a></li>
            <li><a href="http://127.0.0.1:5000/lab6">Шестая лабораторная</a></li>
        </ol>
        </main>

        <footer>
            &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
        </footer>
    </body>
</html>
'''


@lab1.route("/lab1")
def lab():
    return '''
<!doctype html>
<html>
    <head>
        <link rel="stylesheet" href="''' + url_for('static', filename='lab1.css') + '''">
        <title>Чувашова Маргарита Вячеславовна, Лабораторная работа 1</title>
    </head>
    <body>
        <header>
            НГТУ, ФБ, Лабораторная работа 1
        </header>

        <h1>web-сервер на flask</h1>
        <p>
            Flask — фреймворк для создания веб-приложений на языке
            программирования Python, использующий набор инструментов
            Werkzeug, а также шаблонизатор Jinja2. Относится к категории так
            называемых микрофреймворков — минималистичных каркасов веб-приложений, 
            сознательно предоставляющих лишь самые базовые возможности.
        </p>

        <p>
            <a href="http://127.0.0.1:5000/menu">Меню</a>
        </p>

        <h2>Реализованные роуты</h2>
        <ul>
            <li><a href="http://127.0.0.1:5000/lab1/oak">Lab1/oak - Дуб</a></li>
            <li><a href="http://127.0.0.1:5000/lab1/student">Lab1/student - Студент</a></li>
            <li><a href="http://127.0.0.1:5000/lab1/python">Lab1/python - Python</a></li>
            <li><a href="http://127.0.0.1:5000/lab1/cat">Lab1/cat - Котики</a></li>
        </ul>
        <footer>
            &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
        </footer>
    </body>
</html>
'''


@lab1.route('/lab1/oak')
def oak():
    return '''
<!doctype html>
<html>
<head>
    <link rel="stylesheet" href="''' + url_for('static', filename='lab1.css') + '''">
    <title>Дуб</title>
</head>
<body>
    <header>
        НГТУ, ФБ, Лабораторная работа 1
    </header>
    <h1>Дуб</h1>
    <img src="''' + url_for('static', filename='lab1/oak.jpg') + '''" alt="Дуб">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''


@lab1.route("/lab1/student")
def student():
    return '''
<!doctype html>
<html>
<head> 
    <link rel="stylesheet" href="''' + url_for('static', filename='lab1.css') + '''">
</head>
<body>
    <header>
        НГТУ, ФБ, Лабораторная работа 1
    </header>
    <h1>Чувашова Маргарита Вячеславовна</h1>
    <img src="''' + url_for('static', filename='lab1/logo.png') + '''" width="300" alt="Логотип">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''


@lab1.route("/lab1/python")
def python():
    return '''
<!doctype html>
<html>
<head> 
    <link rel="stylesheet" href="''' + url_for('static', filename='lab1.css') + '''">
</head>
<body>
    <header>
        НГТУ, ФБ, Лабораторная работа 1
    </header>
    <h1>Python</h1>
    <p>Python часто воспринимается как удивительно легкий язык программирования благодаря своему простому 
        и читаемому синтаксису...</p>
    <img src="''' + url_for('static', filename='lab1/python.jpg') + '''" width="300" alt="Python">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''


@lab1.route("/lab1/cat")
def cat():
    return '''
<!doctype html>
<html>
<head> 
    <link rel="stylesheet" href="''' + url_for('static', filename='lab1.css') + '''">
</head>
<body>
    <header>
        НГТУ, ФБ, Лабораторная работа 1
    </header>
    <h1>Cat</h1>
    <p>Котики — это удивительные существа, которые славятся своей грациозностью и независимым характером...</p>
    <img src="''' + url_for('static', filename='lab1/cat.png') + '''" width="300" alt="Котик">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''
