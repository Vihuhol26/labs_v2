from flask import Blueprint, render_template, request, redirect, url_for
lab4 = Blueprint('lab4', __name__)

@lab4.route('/lab4/')
def lab():
    return render_template('lab4/lab4.html')

@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')

@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error='Оба поля должны быть заполнены')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)

@lab4.route("/lab4/add", methods=['POST'])
def add():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 else 0
    x2 = int(x2) if x2 else 0
    result = x1 + x2
    return render_template('lab4/div.html', operation="суммирования", x1=x1, x2=x2, result=result)

@lab4.route("/lab4/multiply", methods=['POST'])
def multiply():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 else 1
    x2 = int(x2) if x2 else 1
    result = x1 * x2
    return render_template('lab4/div.html', operation="умножения", x1=x1, x2=x2, result=result)

@lab4.route("/lab4/subtract", methods=['POST'])
def subtract():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error="Оба поля должны быть заполнены для вычитания")
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('lab4/div.html', operation="вычитания", x1=x1, x2=x2, result=result)

@lab4.route("/lab4/power", methods=['POST'])
def power():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error="Оба поля должны быть заполнены для возведения в степень")
    x1 = int(x1)
    x2 = int(x2)
    if x1 == 0 and x2 == 0:
        return render_template('lab4/div.html', error="Оба значения не могут быть равны нулю для возведения в степень")
    result = x1 ** x2
    return render_template('lab4/div.html', operation="возведения в степень", x1=x1, x2=x2, result=result)

tree_count = 0
max_trees = 10 

@lab4.route("/lab4/tree", methods=["GET", "POST"])
def tree():
    global tree_count
    if request.method == "POST":
        operation = request.form.get("operation")
        if operation == "plant" and tree_count < max_trees:
            tree_count += 1
        elif operation == "cut" and tree_count > 0:
            tree_count -= 1
        return redirect(url_for('lab4.tree'))
    return render_template("lab4/tree.html", tree_count=tree_count, max_trees=max_trees) 

if __name__ == "__main__":
    lab4.run(debug=True)

    lab4.secret_key = 'your_secret_key'  

users = [
    {"username": "alex", "password": "123", "name": "Алексей Иванов", "gender": "мужской"},
    {"username": "bob", "password": "456", "name": "Борис Петров", "gender": "мужской"},
    {"username": "anna", "password": "789", "name": "Анна Смирнова", "gender": "женский"}
]

@lab4.route("/lab4/login/", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("lab4/login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    error = None

    # Проверка на пустые поля
    if not username:
        error = "Не введён логин!"
    elif not password:
        error = "Не введён пароль!"

    # Проверка логина и пароля
    if not error:
        for user in users:
            if user["username"] == username and user["password"] == password:
                return render_template("rrr.html", name=user["name"])

        # Ошибка если логин или пароль неверны
        error = "Неверный логин и/или пароль!"

    # Возвращаем пользователя на страницу логина с сохранённым логином и сообщением об ошибке
    return render_template("lab4/login.html", error=error, username=username)

# Добавляем маршрут для страницы регистрации
@lab4.route("/lab4/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        gender = request.form.get("gender")
        
        # Проверка уникальности логина
        if any(user['username'] == username for user in users):
            error = "Этот логин уже занят!"
            return render_template("register.html", error=error)
        
        # Добавление нового пользователя в массив
        users.append({
            'username': username,
            'password': password,
            'name': name,
            'gender': gender
        })
        return redirect(url_for('lab4.login'))
    return redirect(url_for('lab4.login')) 

@lab4.route("/lab4/users")
def users_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("lab4/users_list.html", users=users, current_user=session['username'])

@lab4.route("/lab4/edit/<username>", methods=["GET", "POST"])
def edit_user(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    user = next((u for u in users if u['username'] == username), None)
    if request.method == "POST":
        user['name'] = request.form.get("name")
        user['password'] = request.form.get("password")
        return redirect(url_for('users_list'))
    return render_template("lab4/edit_user.html", user=user)

@lab4.route("/lab4/delete/<username>", methods=["POST"])
def delete_user(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    global users
    users = [u for u in users if u['username'] != username]
    session.pop('username', None) 
    return redirect(url_for('login'))

@lab4.route("/lab4/fridge/", methods=["POST", "GET"])
def fridge():
    if request.method == "GET":
        return render_template("lab4/fridge.html")

    temp = request.form.get("temp")
    if not temp:
        error = "Ошибка: не задана температура!"
        return render_template("lab4/fridge.html", error = error)
    elif int(temp) < -12:
        error = "Не удалось установить температуру — слишком низкое значение!"
        return render_template("lab4/fridge.html", error = error)
    elif int(temp) > -1:
        error = "Не удалось установить температуру — слишком высокое значение!"
        return render_template("lab4/fridge.html", error = error)
    elif int(temp) >= -12 and int(temp) <= -9:
        error = "Установлена температура: " + str(temp) + "°С ❆❆❆"
        return render_template("lab4/temp.html", error = error)
    elif int(temp) >= -8 and int(temp) <= -5:
        error = "Установлена температура: " + str(temp) + "°С ❆❆"
        return render_template("lab4/temp.html", error = error)
    else:
        error = "Установлена температура: " + str(temp) + "°С ❆"
        return render_template("lab4/temp.html", error = error)