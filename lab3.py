from flask import Blueprint, render_template, request, make_response

lab3 = Blueprint('lab3', __name__)

@lab3.route ("/lab3/")
def lab():
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    return render_template("lab3/lab3.html", name=name, name_color=name_color)

@lab3.route('/lab3/cookie')
def cookie():
    return 'установка cookie', 200, {'Set-Cookie': 'name=Alex'}

@lab3.route ('/lab3/del_cookie')
def del_cookie ():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp

@lab3.route("/lab3/form1/")
def form1():
    errors = {}
    user = request.args.get("user")
    if user == "":
        errors["user"] = "Заполните поле!"

    age = request.args.get("age")
    if age == "":
        errors["age"] = "Заполните поле!"
    
    sex = request.args.get("sex")
    return render_template("lab3/form1.html", user = user, age = age, sex = sex, errors = errors)

@lab3.route("/lab3/order/")
def order():
    return render_template("lab3/order.html")

@lab3.route("/lab3/pay/")
def pay():
    price = 0
    drink = request.args.get("drink")
    if drink == "cofee":
        price = 120
    elif drink == "black-tea":
        price = 80
    else:
        price = 70

    if request.args.get("milk") == "on":
        price += 30
    if request.args.get("sugar") == "on":
        price += 10

    return render_template("lab3/pay.html", price = price)


@lab3.route("/lab3/success/")
def success():
    return render_template("lab3/success.html")

@lab3.route("/lab3/train")
def train():
    errors = {}
    return render_template("lab3/train.html", errors = errors)


@lab3.route("/lab3/trainacc")
def trainacc():
    a = 0
    errors = {}
    user_in = request.args.get("user_in")
    user_in = request.args.get("user_in")
    if user_in == "":
        errors["user_in"] = "Заполните поле!"

    user_out = request.args.get("user_out")
    if user_out == "":
        errors["user_out"] = "Заполните поле!"

    user_fio = request.args.get("user_fio")
    if user_fio == "":
        errors["user_fio"] = "Заполните поле!"

    age_pass = request.args.get("age_pass")
    if age_pass == "":
        errors["age_pass"] = "Заполните поле!"
    elif age_pass is not None:
        if int(age_pass) > 120 or int(age_pass) < 18:
            errors["age_pass"] = "От 18 до 120 лет!"
    else:
        a += 1
    
    type_t = request.args.get("type_t")
    if type_t == "child":
        type_t = "Детский"
    if type_t == "human":
        type_t = "Взрослый"

    type_p = request.args.get("type_p")
    if type_p == "down":
        type_p = "нижняя полка"
    elif type_p == "up":
        type_p = "верхняя полка"
    elif type_p == "down_side":
        type_p = "нижняя боковая полка"
    else:
        type_p = "верхняя боковая полка"

    type_b = request.args.get("type_b")
    if type_b == "yes":
        type_b = "Да"
    else:
        type_b = "Нет"

    calen = request.args.get("calen")

    if len(errors) > 0:
        return render_template("lab3/train.html", errors = errors)

    return render_template("lab3/trainacc.html", user_fio = user_fio, user_in = user_in, user_out = user_out, age_pass = age_pass, type_b = type_b,
                           type_p = type_p, type_t = type_t, calen = calen)


products = [
    {'name': 'Смартфон A', 'price': 10000, 'brand': 'Brand A', 'color': 'черный'},
    {'name': 'Смартфон B', 'price': 15000, 'brand': 'Brand B', 'color': 'белый'},
    {'name': 'Смартфон C', 'price': 20000, 'brand': 'Brand A', 'color': 'зеленый'},
    {'name': 'Смартфон D', 'price': 25000, 'brand': 'Brand C', 'color': 'синий'},
    {'name': 'Смартфон E', 'price': 30000, 'brand': 'Brand D', 'color': 'черный'},
    {'name': 'Смартфон F', 'price': 35000, 'brand': 'Brand E', 'color': 'белый'},
    {'name': 'Смартфон G', 'price': 40000, 'brand': 'Brand F', 'color': 'зеленый'},
    {'name': 'Смартфон H', 'price': 45000, 'brand': 'Brand G', 'color': 'синий'},
    {'name': 'Смартфон I', 'price': 50000, 'brand': 'Brand H', 'color': 'черный'},
    {'name': 'Смартфон J', 'price': 55000, 'brand': 'Brand I', 'color': 'белый'},
    {'name': 'Смартфон K', 'price': 60000, 'brand': 'Brand J', 'color': 'зеленый'},
    {'name': 'Смартфон L', 'price': 70000, 'brand': 'Brand K', 'color': 'синий'},
    {'name': 'Смартфон M', 'price': 80000, 'brand': 'Brand L', 'color': 'черный'},
    {'name': 'Смартфон N', 'price': 90000, 'brand': 'Brand M', 'color': 'белый'},
    {'name': 'Смартфон O', 'price': 100000, 'brand': 'Brand N', 'color': 'зеленый'},
    {'name': 'Смартфон P', 'price': 110000, 'brand': 'Brand O', 'color': 'синий'},
    {'name': 'Смартфон Q', 'price': 120000, 'brand': 'Brand P', 'color': 'черный'},
    {'name': 'Смартфон R', 'price': 130000, 'brand': 'Brand Q', 'color': 'белый'},
    {'name': 'Смартфон S', 'price': 140000, 'brand': 'Brand R', 'color': 'зеленый'},
    {'name': 'Смартфон T', 'price': 150000, 'brand': 'Brand S', 'color': 'синий'},
]

@lab3.route("/lab3/range")
def range():
    return render_template('lab3/range.html')

@lab3.route('/search', methods=['POST'])
def search():
    min_price = request.form['min_price']
    max_price = request.form['max_price']

    # Фильтрация товаров по диапазону цен
    filtered_products = [
        product for product in products
        if min_price.isdigit() and max_price.isdigit() and 
        int(min_price) <= product['price'] <= int(max_price)
    ]

    return render_template('lab3/error.html', products=filtered_products)

if __name__ == '__main__':
    lab3.run(debug=True)
