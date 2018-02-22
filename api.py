from flask import Flask, render_template, request, url_for, redirect, session
from flask_mysqldb import MySQL
import datetime
import os


app = Flask(__name__)
mysql = MySQL()
app.config ['MYSQL_HOST']= 'localhost'
app.config ['MYSQL_USER']= 'root'
app.config ['MYSQL_PASSWORD']= ''
app.config ['MYSQL_DB']= 'deltadb'
mysql.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = str(request.form['username'])
    password = str(request.form['password'])

    try:
        cursor = mysql.connect.cursor()
        cursor.execute("SELECT * FROM users WHERE username ='" + username + "' AND passw = '" + password + "'")
        user = cursor.fetchone()
        session['id'] = user[0]
        session['level'] = user[3]
        if user[3] == 1:
            return redirect(url_for('manager_home'))
        elif user[3] == 2:
            return redirect(url_for('kassa_home'))
        else:
            return "nope"
    except Exception as e:
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
   #session ends
   session.pop('id', None)
   return redirect(url_for('index'))


@app.route('/manager', methods=["GET", "POST"])
def manager_home():
    if 'id' in session:
        if session['level'] == 1:
            try:
                return render_template('manager_home.html')
            except Exception as e:
                return e
        else:
            return 'geen acces'
    else:
        return 'nope'


@app.route('/kassa', methods=["GET", "POST"])
def kassa_home():
    if 'id' in session:
        if session['level'] == 2:
            try:
                return render_template('kassa_home.html')
            except Exception as e:
                return e
        else:
            return 'geen acces'
    else:
        return 'nope'


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
