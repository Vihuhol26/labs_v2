from flask import Blueprint, render_template
lab2 = Blueprint('lab2', __name__)

@lab2.route('/lab2/example')
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


@lab2.route('/lab2/')
def lab():
    return render_template('lab2.html')


@lab2.route('/lab2/cats/')
def cats():
    return render_template('cats.html')
