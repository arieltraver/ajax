from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

#separated database functions to avoid repetitive code
def all_movies(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select tt, title, `release`, director, avgrating from movie''')
    movies = curs.fetchall()
    return movies

def getAvg(conn, tt):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select avgRating from movie where tt = %s''', [tt])
    row = curs.fetchone()
    return row['avgRating']

def updateAvg(conn, newAvg, tt):
    curs = dbi.dict_cursor(conn)
    curs.execute('''update movie set avgrating=%s where tt=%s''', [newAvg, tt])
    conn.commit()

def insertRating(conn, uid, tt, rating):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into ratings (uid, tt, rate) values (%s, %s, %s) on duplicate key update rate = %s''', [uid, tt, rating, rating])
    conn.commit()

def deleteRating(conn, uid, tt):
    curs = dbi.dict_cursor(conn)
    curs.execute('''delete from ratings where tt=%s and uid=%s''', [tt, uid])
    conn.commit()

def calcRating(conn, tt):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select tt, avg(rate) from ratings where tt=%s group by tt''', [tt])
    row = curs.fetchone()
    if row == None:
        return 'None'
    else:
        return row['avg(rate)']

@app.route('/')
def index():
    return render_template('movies-base.html')

@app.route('/setUID/', methods=["GET", "POST"])
def setUID():
    if request.method == 'GET':
        return render_template('movies-base.html')
    if request.method == 'POST':
        if 'uid' in request.form:
            UID = request.form['uid']
            session['UID'] = UID
    return redirect(url_for('rate_movie'))

@app.route('/rateMovie/', methods=['GET','POST'])
def rate_movie():
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('rate-movies-list.html', uid=session['UID'], database='tg2_db', movies=all_movies(conn))
    elif request.method == 'POST':
        if not session['UID']:
            print(session['UID'])
            flash("Sorry, you need to login before you can start rating movies!")
            return redirect(url_for('setUID'))
        else:
            uid = session['UID']
            tt = request.form['tt']
            stars = request.form['stars']
            insertRating(conn, uid, tt, stars)
            newRating = calcRating(conn, tt)
            updateAvg(conn, newRating, tt)
            flash('user {} is rating movie {} as {} stars. new average is {}'.format(uid, tt, stars, newRating))
            return redirect(url_for('rate_movie'))

@app.route('/rateMovieAjax/', methods = ['GET', 'POST'])
def rate_movie_ajax():
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('rate-movies-list.html', uid=session['UID'], database='tg2_db', movies=all_movies(conn))
    elif request.method == 'POST':
        if not session['UID']:
            print(session['UID'])
            flash("Sorry, you need to login before you can start rating movies!")
            return redirect(url_for('setUID'))
        else:
            uid = session['UID']
            print(uid)
            tt = request.form['tt']
            stars = request.form['stars']
            insertRating(conn, uid, tt, stars)
            newRating = calcRating(conn, tt)
            updateAvg(conn, newRating, tt)
            return jsonify({'avg': average, 'error': False, 'tt': tt})

@app.route('/rating/', methods=['POST'])
@app.route('/rating/<tt>', methods=['GET', 'PUT', 'DELETE'])
def rating(tt=None):
    if not session['UID']:
        flash('Please log in first!')
        return redirect(url_for('setUID'))
    conn = dbi.connect()
    print(session['UID'])
    uid = session['UID']
    if request.method == 'GET':
        avgRating = getAvg(conn, tt)
        return jsonify({'avg': avgRating, 'error': False, 'tt': tt})
    if request.method == 'POST' or request.method == 'PUT':
        stars = request.form['stars']
        print(stars)
        try:
            tt = request.form['tt']
        except:
            tt = tt
        print(tt)
        insertRating(conn, uid, tt, stars)
        newRating = calcRating(conn, tt)
        updateAvg(conn, newRating, tt)
        return jsonify({'avg': newRating, 'error': False, 'stars': stars, 'tt': tt})
    if request.method == 'DELETE':
        tt = tt
        print(tt)
        deleteRating(conn, uid, tt)
        newRating = calcRating(conn, tt)
        updateAvg(conn, newRating, tt)
        return jsonify({'avg': newRating, 'error': False, 'tt': tt})

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
