import psycopg2
import psycopg2.extras
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_socketio import SocketIO, send
from psycopg2 import Error
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from create_db import create_tables, update_crypto, update_currency, update_news
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'

socketio = SocketIO(app, cors_allowed_origins='*')

def get_db_connection():
    try:
        connection = psycopg2.connect(user=DB_USER,
                                      password=DB_PASSWORD,
                                      host=DB_HOST,
                                      port=DB_PORT,
                                      database=DB_NAME)

        return connection

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


connection = get_db_connection()


@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('login'))


@app.route("/login/", methods=["POST", "GET"])
def login():
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST" and 'email' in request.form and 'password' in request.form:
        user_email = request.form["email"]
        user_password = request.form["password"]

        cursor.execute('''SELECT * FROM users WHERE email = %s''', (user_email,))
        user = cursor.fetchone()

        if user:
            hash_pass = user['hash_password']

            if check_password_hash(hash_pass, user_password):
                session['loggedin'] = True
                session['id'] = user['user_id']
                session['username'] = user['user_name']
                session['surname'] = user['surname']
                session['nickname'] = user['nickname']
                session['email'] = user['email']

                return redirect(url_for('home'))

            else:
                # flash('Incorrect email or password')
                return redirect(url_for('login'))

        else:
            # flash('Account do not exist')
            return redirect(url_for('login'))

    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    global _hash_password
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST" and 'firstName' in request.form and 'lastName' in request.form and 'nickname' \
            in request.form and 'email' in request.form and 'password' in request.form and \
            'rep_password' in request.form:

        user_name = request.form['firstName']
        user_surname = request.form['lastName']
        user_nickname = request.form['nickname']
        user_email = request.form['email']
        user_password = request.form['password']
        user_rep_password = request.form['rep_password']

        if user_password == user_rep_password:
            _hash_password = generate_password_hash(user_password)

        cursor.execute('''SELECT * FROM users WHERE email = %s OR nickname = %s;''', (user_email, user_nickname))
        user = cursor.fetchone()

        if user:
            # flash('Account already exist!')
            return render_template('register.html')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', user_email):
            # flash('Invalid email address!')
            return render_template('register.html')

        elif not re.match(r'[A-Za-z0-9]+', user_name):
            # flash('Username must contain only characters and numbers!')
            return render_template('register.html')

        elif not user_name or not user_surname or not user_nickname or not user_email or not user_password \
                or not user_rep_password:
            # flash('Please, fill out the form!')
            return render_template('register.html')

        else:
            cursor.execute('''INSERT INTO users(user_name, surname, nickname, email, hash_password)
                VALUES (%s, %s, %s, %s, %s);''', (user_name, user_surname, user_nickname, user_email, _hash_password))
            connection.commit()

            # flash('You have successfully registered!')
            return redirect(url_for('login'))

    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        cursor.execute('''SELECT * FROM users WHERE user_id = %s''', [session['id']])
        user = cursor.fetchone()
        return render_template('profile.html', account=user)

    return redirect(url_for('login'))


@app.route('/support')
def support():
    return render_template('support.html')


@socketio.on('message')
def handleMessage(data):
    print(f"Message: {data}")
    send(data, broadcast=True)

    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('''SELECT user_id, user_name, nickname FROM users WHERE user_id = %s''', [session['id']])
    user = cursor.fetchone()
    user_mess = data['msg']
    date = datetime.now().strftime('%H:%M:%S %d-%m-%Y')

    cursor.execute('''INSERT INTO messages(user_id, nickname, user_text, date_time) 
    VALUES (%s, %s, %s, %s);''', (user['user_id'], user['nickname'], user_mess, date))
    connection.commit()


@app.route('/messages/', methods=['POST', 'GET'])
def messages():
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        # if request.method == "POST":
        #     cursor.execute('''SELECT user_id, user_name, nickname FROM users WHERE user_id = %s''', [session['id']])
        #     user = cursor.fetchone()
        #     user_mess = request.form['message']
        #     date = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
        #
        #     if len(user_mess) > 0 and len(user_mess) < 1000:
        #         cursor.execute('''INSERT INTO messages(user_id, nickname, user_text, date_time)
        #         VALUES (%s, %s, %s, %s);''', (user['user_id'], user['nickname'], user_mess, date))
        #         connection.commit()
        #     return redirect(url_for('messages'))

        cursor.execute('''SELECT user_id, user_name, nickname FROM users WHERE user_id = %s''', [session['id']])
        user = cursor.fetchone()

        return render_template('messages.html', username=user['nickname'])

    return redirect(url_for('login'))







    # cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #
    # if 'loggedin' in session:
    #     if request.method == "POST":
    #         cursor.execute('''SELECT user_id, user_name, nickname FROM users WHERE user_id = %s''', [session['id']])
    #         user = cursor.fetchone()
    #         user_mess = request.form['message']
    #         date = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
    #
    #         if len(user_mess) > 0 and len(user_mess) < 1000:
    #             cursor.execute('''INSERT INTO messages(user_id, nickname, user_text, date_time)
    #                 VALUES (%s, %s, %s, %s);''', (user['user_id'], user['nickname'], user_mess, date))
    #             connection.commit()
    #         return redirect(url_for('messages'))
    #
    #     else:
    #         cursor.execute('''SELECT id, nickname, user_text, date_time FROM messages ORDER BY id DESC''')
    #         res_mess = cursor.fetchall()
    #         resp = []
    #         for row in res_mess:
    #             resp.append({'nickname': row['nickname'], 'user_text': row['user_text'], 'date_time': row['date_time']})
    #         return render_template('messages.html', messages=resp)
    #
    # return redirect(url_for('login'))





# @app.route('/1', methods=['GET'])
# def get_currency():
#     if request.method == 'GET':
#         try:
#             cursor = connection.cursor()
#             cursor.execute('''SELECT currency_code, amount, currency_name, currency_value, date_time
#             FROM exchange_currency ORDER BY 5 DESC LIMIT 34;''')
#
#             all_value = cursor.fetchall()
#             cursor.close()
#
#             dict_val = {}
#
#             for elem in all_value:
#                 dict_val[elem[2]] = {'code': elem[0],
#                                      'amount': elem[1],
#                                      'name': elem[2],
#                                      'price': elem[3],
#                                      'time': elem[4]
#                                      }
#
#             currency_js = json.dumps(dict_val, sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ': '))
#
#             return currency_js
#
#         except Exception as e:
#             print(e)
#
#
# @app.route('/2', methods=['GET'])
# def get_crypto():
#     if request.method == 'GET':
#         try:
#             cursor = connection.cursor()
#             cursor.execute('''SELECT crypto_name, crypto_code, price, exchange_price, capitalization, volume,
#                     exchange_per, date_time FROM exchange_crypto ORDER BY 8 DESC LIMIT 46;''')
#
#             all_value = cursor.fetchall()
#             cursor.close()
#
#             dict_val = {}
#
#             for elem in all_value:
#                 dict_val[elem[0]] = {'name': elem[0],
#                                      'code': elem[1],
#                                      'price': float(elem[2]),
#                                      'ex_price': elem[3],
#                                      'capitalization': elem[4],
#                                      'volume': elem[5],
#                                      'ex_per': elem[6],
#                                      'time': elem[7]
#                                      }
#
#             crypto_js = json.dumps(dict_val, sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ': '))
#
#             return crypto_js
#
#         except Exception as e:
#             print(e)
#
#
# @app.route('/3', methods=['GET'])
# def get_news():
#     if request.method == 'GET':
#         try:
#             cursor = connection.cursor()
#             cursor.execute('''SELECT news, links, times, links_images FROM news ORDER BY 3 DESC LIMIT 30;''')
#
#             all_value = cursor.fetchall()
#             cursor.close()
#
#             dict_val = {}
#
#             for elem in all_value:
#                 dict_val[elem[2]] = {'title': str(elem[0]),
#                                      'links': elem[1],
#                                      'time': elem[2],
#                                      'links_images': elem[3]
#                                      }
#             news_js = json.dumps(dict_val, sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ': '))
#
#             return news_js
#
#         except Exception as e:
#             print(e)


# @app.route('/signup', methods=['POST'])
# def sign_up():
#     if request.method == 'POST':
#         # email = request.form.get('email')
#         # first_name = request.form.get('firstname')
#         # last_name = request.form.get('lastname')
#         # password = request.form.get('password')
#         sd = request.json({
#             'email': email,
#             'name': name
#         })


# def schedule_track(connection):
#     # schedule.every().day.at("08:00").do(update_news(connection))
#     # schedule.every().day.at("14:00").do(update_news(connection))
#     # schedule.every().day.at("20:00").do(update_news(connection))
#     # schedule.every().day.at("02:00").do(update_news(connection))
#
#     # schedule.every().day.at("08:00").do(update_currency(connection))
#     # schedule.every().day.at("14:00").do(update_currency(connection))
#     # schedule.every().day.at("20:00").do(update_currency(connection))
#     # schedule.every().day.at("02:00").do(update_currency(connection))
#
#     schedule.every(20).seconds.do(update_currency, connection=connection)
#
#     # schedule.every().day.at("08:00").do(update_crypto(connection))
#     # schedule.every().day.at("14:00").do(update_crypto(connection))
#     # schedule.every().day.at("20:00").do(update_crypto(connection))
#     # schedule.every().day.at("02:00").do(update_crypto(connection))
#
#     while True:
#         schedule.run_pending()


create_tables(connection)
# schedule_track(connection)

# update_crypto(connection)
# update_currency(connection)


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app)

