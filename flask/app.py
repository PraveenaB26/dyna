from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
#DATABASE = "db.sqlite3"

ORS(app)
# ✅ Use absolute path for the database
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, "db.sqlite3")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # return rows as dict-like objects
    return conn


# --- GET endpoint: fetch all users ---
@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    users = conn.execute("SELECT id, name, email FROM users").fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])


# --- GET endpoint with ID ---
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    return jsonify({"error": "User not found"}), 404


# --- POST endpoint: create a new user ---
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Missing name or email"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "User created", "user_id": new_id}), 201


# --- PUT endpoint: update existing user ---
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id)
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()

    if updated_rows == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User updated"})

from flask import render_template

@app.route("/")
def home():
    return render_template("app.html")

if __name__ == "__main__":
    # Initialize DB (only once)
    conn = sqlite3.connect(DATABASE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.close()

    app.run(debug=True,host="0.0.0.0")
