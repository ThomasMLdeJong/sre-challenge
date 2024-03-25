import sqlite3
import logging
from flask import Flask, session, redirect, url_for, request, render_template, abort
import bcrypt
import os
import psycopg2


app = Flask(__name__)
app.secret_key = b"192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf"
app.logger.setLevel(logging.INFO)


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def is_authenticated():
    return "username" in session


def authenticate(username, password):
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Get the database credentials from Kubernetes secrets or configmap
    db_host = os.getenv("DB_HOST")  # Assuming you have this environment variable set
    db_port = os.getenv("DB_PORT", "5432")  # Assuming PostgreSQL default port
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    # Connect to PostgreSQL database
    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    cursor = connection.cursor()

    # Use a parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user:
        # Verify hashed password
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            app.logger.info(f"The user '{username}' logged in successfully")
            session["username"] = username
            connection.commit()
            cursor.close()
            connection.close()
            return True
        else:
            app.logger.warning(f"Invalid password for user '{username}'")
            # Provide more user-friendly feedback
            cursor.close()
            connection.close()
            raise ValueError("Invalid username or password")
    else:
        app.logger.warning(f"User '{username}' not found")
        cursor.close()
        connection.close()
        raise ValueError("Invalid username or password")

@app.route("/")
def index():
    return render_template("index.html", is_authenticated=is_authenticated())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if authenticate(username, password):
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)