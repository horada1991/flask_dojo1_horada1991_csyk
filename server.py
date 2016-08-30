from flask import Flask, g, request
import sqlite3

app = Flask('Flask Dojo')
DATABASE = 'database.db'


# DB connect
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def setup_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print('Initialized the database.')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/request-counter', methods=['POST', 'GET'])
def req_counter():
    db = get_db()
    cur = db.execute("""SELECT counter from flask_dojo WHERE method=?""", [request.method])
    data = cur.fetchall()
    print(data)
    if not data:
        db.execute("""INSERT INTO flask_dojo (method, counter) VALUES (?, 1)""", [request.method])
    else:
        db.execute("""UPDATE flask_dojo SET counter=? WHERE method=?""", [data[0][0] + 1, request.method])
    db.commit()


with app.app_context():
    setup_db()
    req_counter()