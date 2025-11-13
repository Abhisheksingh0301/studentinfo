import pyodbc
from flask import g

# CONNECTING DATA FROM COESERVER
DB_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'COESERVER',    
    'database': 'Exam',        
    'username': 'abhi',           
    'password': 'abhi',           
    'trust_cert': 'yes'                      
}

def get_connection_string():
    return (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate={DB_CONFIG['trust_cert']};"
    )

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        conn_str = get_connection_string()
        db = g._database = pyodbc.connect(conn_str)
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Since your DB already exists, you don’t need to create tables
def init_db():
    return "Existing SQL Server database connection initialized successfully!"
