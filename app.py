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
    if request.method == 'GET':
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''select * from movie''')
        rows = curs.fetchall()
        #check in console
        print(rows[0])
        return render_template('rate-movies-list.html', uid=session['UID'], database='tg2_db', movies=rows)
    elif request.method == 'POST':
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''insert into ratings values (%s, %s, %s) on duplicate key update rate = %s;''', 
                        [session['UID'], request.form['tt'], request.form['stars'], request.form['stars']])
        curs.execute('''select avg(rate) as newAvg from ratings where tt=%s group by tt''', [request.form['tt']])
        newAvg = curs.fetchone()['newAvg']
        print(newAvg)
        curs.execute('''update movie set avgrating=%s where tt=%s''', [float(newAvg), request.form['tt']])
        conn.commit()

        curs.execute('''select avgrating from movie where tt=%s''', [request.form['tt']])
        row = curs.fetchone()

        curs.execute('''select * from movie''')
        rows = curs.fetchall()
        #STOPPED HERE: ISSUE IS THAT WHEN YOU RELOAD NEW RATING WON'T SHOW IN COLUMN 
        
        print(row)
        flash('user {} is rating movie {} as {} stars. new average is {}'.format(session['UID'], request.form['tt'], request.form['stars'], row['avgrating']))
        return render_template('rate-movies-list.html', uid=session['UID'], database='tg2_db', movies=rows)

@app.route('/rateMovieAjax/')
def rate_movie_ajax():
    return render_template('movies-base.html')

@app.route('/rating/', methods=['POST'])
def rating(uid):
    tt = request.form['tt']
    stars = request.form['stars']
    return {'tt': tt, 'stars': stars}

# @app.route('/rating/<tt>/' methods=['GET', 'PUT', 'DELETE'])
# def rating(tt):
#     conn = dbi.connect()
#     curs = dbi.dict_cursor(conn)
#     if request.method == 'GET':
#         curs.execute('''select rating from movie where tt=%s''', [tt])
#         currentAvg = curs.fetchone()
#         return currentAvg
#     elif request.method == 'PUT':
#         stars = request.form['stars']
#         tt = tt
#         currentAvg = url_for('rating', tt=tt)
#         newAvg = (currentAvg + stars)/2
#         curs.execute('''insert into movie (rating) values (%s)''', [newAvg]
#         conn.commit()
#         return 
#     return render_template('movies-base.html')

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
