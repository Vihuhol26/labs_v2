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
