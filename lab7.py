from flask import Blueprint, render_template, request, make_response, redirect, session, url_for

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def lab():
    return render_template('lab7/lab7.html')

films = [
    {
        "title": "Inception",
        "title_ru": "Начало",
        "year": 2010,
        "description": "Дом Кобб — искусный вор, лучший в опасном искусстве извлечения: \
        он крадет ценные секреты из глубин подсознания во время сна, когда человеческий \
        разум наиболее уязвим. Теперь Коббу предстоит выполнить свою последнюю миссию, \
        которая может вернуть ему его жизнь, но только если он сможет осуществить \
        невозможное — инцепцию. Вместо того чтобы украсть идею, он должен \
        внедрить ее. Если он преуспеет, это станет идеальным преступлением."
    },
    {
        "title": "Interstellar",
        "title_ru": "Интерстеллар",
        "year": 2014,
        "description": "Когда засуха приводит человечество к продовольственному кризису, \
        команда исследователей и ученых отправляется сквозь червоточину (которая предположительно \
        соединяет области пространства-времени через большое расстояние) в путешествие, \
        чтобы превзойти прежние ограничения космических путешествий человека и найти планету \
        с подходящими для человечества условиями."
    },
    {
        "title": "The Social Network",
        "title_ru": "Социальная сеть",
        "year": 2010,
        "description": "История создания социальной сети Facebook и \
        связанных с этим судебных разбирательств. Фильм рассказывает о том, \
        как Марк Цукерберг, будучи студентом Гарварда, создал одну из самых \
        популярных социальных сетей в мире, и о конфликтах, которые возникли \
        на этом пути."
    },
    {
        "title": "The Grand Budapest Hotel",
        "title_ru": "Отель «Гранд Будапешт»",
        "year": 2014,
        "description": "Фильм рассказывает о приключениях легендарного консьержа \
        отеля «Гранд Будапешт» Густава и его юного протеже Зеро Мустафы. \
        В центре сюжета — кража бесценного произведения искусства и битва за \
        огромное состояние, оставленное одной из постоялиц отеля."
    },
    {
        "title": "Mad Max: Fury Road",
        "title_ru": "Безумный Макс: Дорога ярости",
        "year": 2015,
        "description": "В постапокалиптическом мире, где царит хаос, \
        Макс присоединяется к группе беглецов, которые пытаются спастись \
        от тирана Несмертного Джо. Вместе с воительницей Фуриозой они \
        отправляются в опасное путешествие по пустыне, чтобы найти \
        безопасное место."
    },
]


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if 0 <= id < len(films):
        return films[id]
    else:
        return ({'error': 'Фильм не найден'}), 404
    
@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return films

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if 0 <= id < len(films):
        del films[id]
        return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT']) 
def put_film(id):
    film = request.get_json()
    # Проверка, существует ли фильм с указанным id
    if id < 0 or id >= len(films):
        return {'error': 'Фильм с указанным id не найден'}, 404

    # Проверки для обновления фильма
    if not film.get('title_ru'):
        return {'title_ru': 'Русское название обязательно'}, 400

    if not film.get('description'):
        return {'description': 'Описание обязательно'}, 400

    if film.get('year', 0) < 1895 or film.get('year', 0) > 2023:
        return {'year': 'Год должен быть между 1895 и 2023'}, 400

    if not film.get('title') and film.get('title_ru'):
        film['title'] = film['title_ru']

    # Обновление фильма
    films[id] = film
    return film, 200

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()

    # Проверки для добавления фильма
    if not film.get('title_ru'):
        return {'title_ru': 'Русское название обязательно'}, 400

    if not film.get('description') or len(film['description']) > 2000:
        return {'description': 'Описание обязательно и не может превышать 2000 символов'}, 400

    if film.get('year', 0) < 1895 or film.get('year', 0) > 2023:
        return {'year': 'Год должен быть между 1895 и 2023'}, 400

    if not film.get('title') and film.get('title_ru'):
        film['title'] = film['title_ru']

    # Добавление фильма в список
    films.append(film)
    return film, 201
    