import os
import sqlite3
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_ME")

conn = sqlite3.connect("store.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    image TEXT,
    description TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    items TEXT,
    total REAL,
    status TEXT
)
""")
conn.commit()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error":"login required"}), 401
        return f(*args, **kwargs)
    return wrap

@app.route('/')
def home():
    return "STORE API RUNNING"

@app.route('/api/products')
def products():
    cursor.execute("SELECT * FROM products")
    return jsonify(cursor.fetchall())

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",
                   (data['username'], generate_password_hash(data['password'])))
    conn.commit()
    return jsonify({"status":"ok"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    cursor.execute("SELECT password FROM users WHERE username=?",(data['username'],))
    u = cursor.fetchone()
    if u and check_password_hash(u[0], data['password']):
        session['user'] = data['username']
        return jsonify({"status":"logged"})
    return jsonify({"error":"invalid"}), 401

@app.route('/api/checkout', methods=['POST'])
@login_required
def checkout():
    return jsonify({"status":"order created"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
