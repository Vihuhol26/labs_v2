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
