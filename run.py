from flask import Flask
from datetime import datetime
from db import close_db, init_db
from auth_db import close_auth_db, init_auth_db

# ----------------------------
# 1️⃣ Create the Flask app
# ----------------------------
app = Flask(__name__, template_folder='app/templates')
app.secret_key = 'abhishek0301'  # Replace with a strong secret key

# ----------------------------
# 2️⃣ Register blueprints
# ----------------------------
from app.routes import main
app.register_blueprint(main)

# ----------------------------
# 3️⃣ Teardown databases
# ----------------------------
@app.teardown_appcontext
def teardown_db(exception):
    close_db()         # SQL Server
    close_auth_db()    # SQLite

# ----------------------------
# 4️⃣ Routes for initializing DBs
# ----------------------------
@app.route('/init-db')
def initialize_database():
    return init_db()  # SQL Server

@app.route('/init-auth-db')     # to generate auth.db with users table
def initialize_auth_database():
    return init_auth_db()  # SQLite

# ----------------------------
# 5️⃣ Jinja filter example
# ----------------------------
def format_dmy(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime('%d-%b-%y')
    except Exception:
        return value

app.jinja_env.filters['format_dmy'] = format_dmy

# ----------------------------
# 6️⃣ Start the app
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5050)
