from flask import Flask, render_template, session, request, url_for, redirect, flash
from mysql_db import MySQL
from auth import User, is_admin, UsersPolicy
import mysql.connector as connector
from collections import namedtuple
import flask_login
import os

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')
app.secret_key = os.urandom(26)

mysql = MySQL(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице необходимо авторизироваться.'

def load_roles():
    cursor = mysql.connection().cursor(named_tuple=True)
    cursor.execute('select id,name from roles;')
    roles = cursor.fetchall()
    cursor.close()
    return roles

def login_is_exist(login):
    cursor = mysql.connection().cursor(named_tuple=True)
    cursor.execute('select * from users_exam where login=%s;', (login,))
    exist = cursor.fetchone()
    cursor.close()
    if not exist:
        return False
    return True

def get(query,fetch):
    '''parametr query is making a string for database\n\
       \nparametr fetch choosing between all and one by 0 and 1\n
       actualy after 4 hours i gotta say that you better\n
       not to use this function with fetchone()'''
    cursor = mysql.connection().cursor(named_tuple=True)
    cursor.execute(query)
    fetchDict = {
        0: cursor.fetchall(),
        1: cursor.fetchone()
    }
    result = fetchDict[fetch]
    cursor.close()
    return result

@app.route('/')
def index():
    books = get('select * from book',0)

    return render_template('index.html', books=books)

@login_manager.user_loader
def load_user(id):
    cursor = mysql.connection().cursor(named_tuple=True)
    cursor.execute('select * from exusers where id=%s;', (id,))
    user_from_db = cursor.fetchone()
    cursor.close()
    if user_from_db:
        user = User()
        user.id = user_from_db.id
        user.login = user_from_db.login
        user.fio = user_from_db.fio
        user.role = user_from_db.role
        return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('login.html')

    if request.method == 'POST':
        if request.form.get('username') and request.form.get('password'):
            cursor = mysql.connection().cursor(named_tuple=True)
            cursor.execute('select id, login, fio, role from exusers where login=%s and password=%s;',
                           (request.form.get('username'), request.form.get('password'),))
            user_from_db = cursor.fetchone()
            cursor.close()
            if user_from_db:
                user = User()
                user.id = user_from_db.id
                user.login = user_from_db.login
                user.fio = user_from_db.fio
                user.role = user_from_db.role

                flask_login.login_user(user, remember=True)
                flash('Вы успешно аутентифицированы.', 'success')
                session['username'] = user.login
                return redirect(url_for('index'))
        else:
            flash('Введены неверные логин и/или пароль.', 'danger')
    return render_template('login.html')

@app.route('/jour', methods=['GET', 'POST'])
@flask_login.login_required
def jour():
    jour = get('select * from jour', 0)
    return render_template('jour.html',jour=jour)

@app.route('/add', methods=['GET','POST'])
@flask_login.login_required
def add():
    if request.args.get('id'):
        cursor = mysql.connection().cursor(named_tuple=True)
        cursor.execute('select id, name, author, year, sum from book where id=%s;',(request.args.get('id'),))
        book = cursor.fetchone()
        cursor.close()
        return render_template('add.html', book=book)

    books = get('select * from book',0)
    return render_template('add.html', books=books)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    session.pop('login', None)
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html')