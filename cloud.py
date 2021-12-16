from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random
import bcrypt

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('cloud.html')

@app.route('/join/', methods=["POST"])
def join():
    conn = dbi.connect()
    curs = dbi.cursor(conn)

    username = request.form.get('username')
    passwd = request.form.get('password')
    print(username)
    print(passwd)
    hashed = bcrypt.hashpw(passwd.encode('utf-8'),
                           bcrypt.gensalt())
    stored = hashed.decode('utf-8')
    print(passwd, type(passwd), hashed, stored)
    try:
        curs.execute('''INSERT INTO userpass(username,hashed)
                        VALUES(%s,%s)''',
                     [username, stored])
        conn.commit()
        return jsonify({'error': False, 'uid': username})
    except Exception as err:
        error = 'That username is taken: {}'.format(repr(err))
        return jsonify({'error': True, 'errmsg': error})

@app.route('/login/', methods=["POST"])
def login():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    username = request.form.get('username')
    passwd = request.form.get('password')
    
    curs.execute('''SELECT username,hashed
                    FROM userpass
                    WHERE username = %s''',
                 [username])
    row = curs.fetchone()
    if row is None:
        error = "Hmm, that login is incorrect. Try again or join!"
        return jsonify({'error': True, 'errmsg': error})
    
    stored = row['hashed']
    hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),
                            stored.encode('utf-8'))
    hashed2_str = hashed2.decode('utf-8')
    if hashed2_str == stored:
        session['username'] = username
        session['logged_in'] = True
        return jsonify({'error': False})
    else:
        error = 'login incorrect. Try again or join'
        return jsonify({'error': True, 'errmsg': error})

@app.route('/<username>/<key>', methods = ['GET', 'PUT', 'DELETE'])
def user(username, key):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    if request.method == 'GET':
        curs.execute('''select userVal from userKeyVal where username=%s AND userKey=%s''', 
                        [username, key])
        value = curs.fetchone()['userVal']
        return jsonify({'error': False, 'value': value})
    if request.method == 'PUT':
        value = request.form['value']
        print(value)
        curs.execute('''insert into userKeyVal values (%s, %s, %s)''', 
                        [username, key, value])
        conn.commit()
        return jsonify({'error': False})
    if request.method == 'DELETE':
        curs.execute('''delete from userKeyVal where username=%s AND userKey=%s''', 
                        [username, key])
        conn.commit()
        return jsonify({'error': False})

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'tg2_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
