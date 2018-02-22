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


@app.route('/kassa/transacties', methods=["GET", "POST"])
def kassa_coins():
    return render_template('kassa_coins.html')


@app.route('/kassa/transacties/countcoins', methods=["GET", "POST"])
def countcoins():
    in1 = request.form['in1'];
    in2 = request.form['in2'];
    in3 = request.form['in3'];
    in4 = request.form['in4'];
    in5 = request.form['in5'];
    in6 = request.form['in6'];

    out1 = round(int(in1) * 2.50, 2);
    out2 = round(int(in2) * 1.00, 2);
    out3 = round(int(in3) * 0.25, 2);
    out4 = round(int(in4) * 0.10, 2);
    out5 = round(int(in5) * 0.05, 2);
    out6 = round(int(in6) * 0.01, 2);

    tot = out1 + out2 + out3 + out4 + out5 + out6
    tot = str(round(tot, 2))

    try:
        ses_id = str(session['id'])
        cursor = mysql.connect.cursor()
        today = datetime.datetime.now().date()
        date = str(today)
        cursor.execute(
                "SELECT COUNT(*) from coin where date='" + date + "' AND user_id='" + ses_id + "'")
        result = cursor.fetchone()
        number_of_rows = result[0]

        if number_of_rows == 0:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO coin (user_id, 1cent, 5cent, 10cent, 25cent, 100cent, 250cent,total, date)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (ses_id, in6, in5, in4, in3, in2, in1, tot, date))
            mysql.connection.commit()
            return render_template('kassa_coins.html', out1=out1, out2=out2, out3=out3,
                                   out4=out4, out5=out5, out6=out6, tot=tot)
        else:
            cur = mysql.connection.cursor()
            cur.execute("""
               UPDATE coin
               SET 1cent=1cent+%s, 5cent=5cent+%s, 10cent=10cent+%s, 25cent=25cent+%s, 100cent=100cent+%s, 
               250cent=250cent+%s,total=total+%s
               WHERE user_id=%s AND date=%s""",
                        (in6, in5, in4, in3, in2, in1, tot, ses_id, date))
            mysql.connection.commit()
            return render_template('kassa_coins.html', out1=out1, out2=out2, out3=out3,
                                   out4=out4, out5=out5, out6=out6, tot=tot)
    except Exception as e:
        return redirect(url_for('kassa_home'))


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
