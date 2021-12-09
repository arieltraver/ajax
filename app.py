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
        #print(rows[0])
        return render_template('rate-movies-list.html', uid=session['UID'], database='tg2_db', movies=rows)
    elif request.method == 'POST':
        if not session['UID']:
            print(session['UID'])
            flash("Sorry, you need to login before you can start rating movies!")
            return redirect(url_for('setUID'))
        else:
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute('''insert into ratings values (%s, %s, %s) on duplicate key update rate = %s;''', 
                            [session['UID'], request.form['tt'], request.form['stars'], request.form['stars']])
            curs.execute('''select avg(rate) as newAvg from ratings where tt=%s group by tt''', [request.form['tt']])
            newAvg = curs.fetchone()['newAvg']
            curs.execute('''update movie set avgrating=%s where tt=%s''', [float(newAvg), request.form['tt']])
            conn.commit()

            curs.execute('''select avgrating from movie where tt=%s''', [request.form['tt']])
            row = curs.fetchone()

            curs.execute('''select * from movie''')
            rows = curs.fetchall()
            
            flash('user {} is rating movie {} as {} stars. new average is {}'.format(session['UID'], request.form['tt'], request.form['stars'], row['avgrating']))
            return render_template('rate-movies-list.html', uid=session['UID'], database='tg2_db', movies=rows)

@app.route('/rateMovieAjax/', methods = ['GET', 'POST'])
def rate_movie_ajax():
    if request.method == 'GET':
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''select * from movie''')
        rows = curs.fetchall()
        #check in console
        #print(rows[0])
        return render_template('rate-movies-list.html', uid=session['UID'], database='tg2_db', movies=rows)
    elif request.method == 'POST':
        if not session['UID']:
            print(session['UID'])
            return redirect(url_for('setUID'))
        else:
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute('''insert into ratings values (%s, %s, %s) on duplicate key update rate = %s;''', 
                            [session['UID'], request.form['tt'], request.form['stars'], request.form['stars']])
            curs.execute('''select avg(rate) as newAvg from ratings where tt=%s group by tt''', [request.form['tt']])
            newAvg = curs.fetchone()['newAvg']
            curs.execute('''update movie set avgrating=%s where tt=%s''', [float(newAvg), request.form['tt']])
            conn.commit()

            curs.execute('''select avgrating from movie where tt=%s''', [request.form['tt']])
            row = curs.fetchone()

            tt = request.form['tt']
            average = row['avgrating']
            print(average)
            print(tt)
            return jsonify({'avg': average, 'tt': tt})

#pretty sure these next 2 are wrong, i think i'm a little confused as to what the purpose
#of the REST functions is and also how exactly we're expected to implement them

@app.route('/rating/', methods=['POST'])
def rating():
    if not session['UID']:
        print(session['UID'])
        return redirect(url_for('setUID'))
    else:
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''insert into ratings values (%s, %s, %s) on duplicate key update rate = %s;''', 
                            [session['UID'], request.form['tt'], request.form['stars'], request.form['stars']])
        curs.execute('''select avg(rate) as newAvg from ratings where tt=%s group by tt''', [request.form['tt']])
        newAvg = curs.fetchone()['newAvg']
        curs.execute('''update movie set avgrating=%s where tt=%s''', [float(newAvg), request.form['tt']])
        conn.commit()

        curs.execute('''select avgrating from movie where tt=%s''', [request.form['tt']])
        row = curs.fetchone()

        tt = request.form['tt']
        average = row['avgrating']
        print(average)
        print(tt)
        return {'tt': tt, 'avg': average}

@app.route('/rating/<tt>', methods = ['GET', 'PUT', 'DELETE'])
def rating_tt(tt):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    if request.method == 'GET':
        curs.execute('''select avgrating from movie where tt=%s''', [tt])
        newAvg = curs.fetchone()['avgrating']
        return newAvg
    elif request.method == 'PUT':
        stars = request.form['stars']
        curs.execute('''insert into ratings values (%s, %s, %s) on duplicate key update rate = %s;''', 
                        [session['UID'], tt, request.form['stars'], request.form['stars']]) 
        curs.execute('''select avg(rate) as newAvg from ratings where tt=%s group by tt''', [tt])
        newAvg = curs.fetchone()['newAvg']
        return newAvg
    else:
        curs.execute('''delete from ratings where tt=%s''', [tt])
        curs.execute('''select avg(rate) as newAvg from ratings where tt=%s group by tt''', [tt])
        newAvg = curs.fetchone()['newAvg']
        return newAvg

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
