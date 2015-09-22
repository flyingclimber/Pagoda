#!/usr/local/bin/python

'''
DB Engine
'''

import sqlite3
from datetime import datetime
from os import path

DB = 'pagoda.db'
conn = None

def create_db():
    '''
    create_db - Creates a new pagoda db
    '''
    global conn

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE reviews
        (id INTEGER PRIMARY KEY, game VARCHAR, ign REAL, meta REAL)''')
    cur.execute('''CREATE TABLE updates
        (id INTEGER PRIMARY KEY, status, date DATE)''')
    cur.execute("INSERT INTO updates (status, date) VALUES (?,?)",
        ('Created', datetime.now()))
    conn.commit()
    conn.close()

def init_db():
    '''
    init_orders_db - initialize the db and create it if it doesn't exist
    '''
    global conn

    if not path.exists(DB):
        create_db()
    if not conn:
        conn = sqlite3.connect(DB)

def get_score(title):
    '''
    get_score - Given a title return all of it's scores
    '''
    conn = sqlite3.connect(DB)
    conn.text_factory = str
    cur = conn.cursor()

    res = cur.execute("SELECT ign FROM reviews WHERE game = ?", (title,))

    if res.rowcount == 0:
        return False
    else:
        return res.fetchone()

def update_score(title, ign):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("INSERT INTO reviews (game, ign) values (?, ?)",
                (title, ign))
    conn.commit()
    conn.close()
