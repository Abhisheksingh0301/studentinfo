import sqlite3
from flask import g

AUTH_DATABASE = "auth.db"

def get_auth_db():
    if "auth_db" not in g:
        g.auth_db = sqlite3.connect(AUTH_DATABASE)
        g.auth_db.row_factory = sqlite3.Row
    return g.auth_db

def close_auth_db(e=None):
    db = g.pop("auth_db", None)
    if db is not None:
        db.close()

def init_auth_db():
    db = get_auth_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.commit()
    return "Auth database initialized!"
