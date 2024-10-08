from flask import Flask, redirect, url_for, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/index")
def start():
    return redirect("/menu", code=302)

@app.route("/menu")
def menu():
        return '''
<!doctype html>
<html>
    <head>
        <link rel="stylesheet" href="''' + url_for('static', filename='lab1.css') + '''">
        <title>НГТУ, ФБ, Лабораторные работы</title>
    </head>
    <body>
        <header>
            НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных
        </header>

        <main>

        <ol>
            <li><a href="http://127.0.0.1:5000/lab1">Первая лабораторная</a></li>
            <li><a href="http://127.0.0.1:5000/lab2">Вторая лабораторная</a></li>
        </ol>

        </main>

        <footer>
            &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
        </footer>
    </body>
</html>
'''

@app.route("/lab1")
def lab1():
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
        </P>

        <p>
            <a href="http://127.0.0.1:5000">Меню</a>
        </p>

        <h2>Реализованные роуты</h2>

        <p>
            <li><a href="http://127.0.0.1:5000/lab1/oak">Lab1/oak - Дуб</a></li>
            <li><a href="http://127.0.0.1:5000/lab1/student">Lab1/student - Студент</li>
            <li><a href="http://127.0.0.1:5000/lab1/python">Lab1/python - Python</li>
            <li><a href="http://127.0.0.1:5000/lab1/cat">Lab1/cat - Котики</li>
        </p>
        <footer>
            &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
        </footer>
    </body>
</html>
'''

@app.route('/lab1/oak')
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
    <img src="''' + url_for('static', filename='oak.jpg') + '''">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''

@app.route("/lab1/student")
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
    <img src="''' + url_for('static', filename='logo.png') + '''" width="300" height="auto">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''

@app.route("/lab1/python")
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

    <p>
        Python часто воспринимается как удивительно легкий язык программирования благодаря своему простому 
        и читаемому синтаксису. Новички могут быстро освоить основы, что позволяет им сосредоточиться на логике программирования, 
        а не на сложном синтаксисе. Это делает Python отличным выбором для людей, только начинающих свой путь в программировании.
    </p>

    <p>
        Богатая экосистема библиотек и фреймворков также добавляет привлекательности: разработка веб-приложений, работа с данными и 
        машинное обучение становятся доступнее благодаря готовым решениям. Это позволяет разработчикам достигать быстрых результатов 
        и уменьшает время на кодирование.
    </p>

    <p>
        Однако стоит помнить, что такая "легкость" может быть обманчивой. Хотя язык интуитивно понятен, для достижения серьезных результатов 
        требуется глубокое понимание его особенностей и принципов. Python позволяет реализовать множество идей, но, как и в любом другом языке, 
        успех зависит от практики и упорного труда.
    </p>

    <img src="''' + url_for('static', filename='python.jpg') + '''" width="300" height="auto">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''

@app.route("/lab1/cat")
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

    <p>
       Котики — это удивительные существа, которые славятся своей грациозностью и независимым характером. Их мягкое мурчание и игривое поведение 
       способны поднять настроение даже в самый хмурый день. Каждое движение кота наполнено элегантностью, а его игривость делает их замечательными 
       спутниками для людей любых возрастов. 
    </p>

    <p>
    Любители котиков знают, что у этих пушистиков есть не только игривость, но и большое разнообразие характеров. От спокойных и ласковых до более 
    независимых и озорных — каждый котик уникален. Они могут быть настоящими компаньонами, которые проводят время рядом с вами, или же предпочитают 
    самостоятельно исследовать окружающий мир. Тем не менее, каждое взаимодействие с котиком — это маленькое удовольствие, которое приносит радость в повседневную жизнь.   
    </p>

    <p>
    Не стоит забывать и о том, что котики известны своим умением создавать уют в доме. ИхPresence добавляет теплоты и комфорта, а забавные привычки
    и милые выходки всегда вызывают улыбку у хозяев. Котики учат нас быть более внимательными к мелочам и ценить моменты радости, которые они приносят. 
    Ведь в конце концов, что может быть лучше, чем уютный вечер с любимым котом на коленях?  
    </p>

    <img src="''' + url_for('static', filename='cat.png') + '''" width="300" height="auto">
    <footer>
        &copy; Чувашова Маргарита Вячеславовна, ФБИ-23, 3 курс, 2024
    </footer>
</body>
</html>
'''
@app.route('/lab2/example')
def example():
    name, number, group, course = 'Chuvashova Margarita', 2, 'ФБИ-23', 3
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321}
        ]
    books = [
        {'author': 'Лев Толстой', 'title': 'Война и мир', 'genre': 'Исторический роман', 'pages': 1200},
        {'author': 'Федор Достоевский', 'title': 'Преступление и наказание', 'genre': 'Роман', 'pages': 600},
        {'author': 'Антуан де Сент-Экзюпери', 'title': 'Маленький принц', 'genre': 'Фантазия', 'pages': 100},
        {'author': 'Габриэль Гарсиа Маркес', 'title': 'Сто лет одиночества', 'genre': 'Магический реализм', 'pages': 450},
        {'author': 'Джордж Оруэлл', 'title': '1984', 'genre': 'Дистопия', 'pages': 328},
        {'author': 'Достоевский Ф.', 'title': 'Идиот', 'genre': 'Роман', 'pages': 700},
        {'author': 'Гарри Поттер', 'title': 'Гарри Поттер и философский камень', 'genre': 'Фэнтези', 'pages': 223},
        {'author': 'Джейн Остин', 'title': 'Гордость и предубеждение', 'genre': 'Роман', 'pages': 432},
        {'author': 'Марк Твен', 'title': 'Приключения Гекльберри Финна', 'genre': 'Приключения', 'pages': 366},
        {'author': 'Джон Р. Р. Толкин', 'title': 'Властелин колец', 'genre': 'Фэнтези', 'pages': 1178}
        ]
    return render_template('example.html', name=name, number=number, 
    group=group, course=course, fruits=fruits, books=books)

@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/cats/')
def cats():
    return render_template('cats.html')
