from app import app
from flask import redirect
from app import app
from flask import redirect, render_template


@app.route("/")
def home():
    return render_template('index.html', css_file='static/css/stylesinicio.css')


@app.route('/menuLinea')
def menuLinea():


    return render_template('test.html', css_file='static/css/styles.css')


# @app.route('/index')
# def index():
#     return "Hello, World!"
