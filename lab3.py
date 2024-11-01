from flask import Blueprint, render_template, request, make_response

lab3 = Blueprint('lab3', __name__)

@lab3.route('/lab3/')
def lab():
    return render_template("lab3/lab3.html")
