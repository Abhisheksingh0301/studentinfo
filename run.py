from flask import Flask
from datetime import datetime
from db import close_db, init_db

# ✅ Create the Flask app first
app = Flask(__name__, template_folder='app/templates')
app.secret_key = 'abhishek0301'  # Replace with a strong secret key

# ✅ Import and register blueprints *after* creating app
from app.routes import main
app.register_blueprint(main)

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

# ✅ Define routes after app is created
@app.route('/init-db')
def initialize_database():
    return init_db()  # Or "Database connected!" if you skipped creating tables

# ✅ Example Jinja filter
def format_dmy(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime('%d-%b-%y')
    except Exception:
        return value

app.jinja_env.filters['format_dmy'] = format_dmy

# ✅ Start the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5050)
