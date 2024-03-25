import os
import logging
import bcrypt
import psycopg2
from flask import Flask, session, redirect, url_for, request, render_template

app = Flask(__name__)
app.secret_key = b"192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf"
app.logger.setLevel(logging.INFO)

def is_authenticated():
    """
    Controleer of de user geautenticeerd is.
    """
    return "username" in session

def get_database_credentials():
    """
    Opvragen van database credentials
    """
    return {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432")
    }

def authenticate(username, password):
    """ 
    controleer of de username en password die worden gegeven door de gebruiker,
    overeen komen met dat wat in de database staat.
    """
    try:
        db_credentials = get_database_credentials()

        connection = psycopg2.connect(**db_credentials)
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                app.logger.info(f"The user '{username}' logged in successfully")
                session["username"] = username
                return True
            else:
                app.logger.warning(f"Invalid password for user '{username}'")
                raise ValueError("Invalid username or password")
        else:
            app.logger.warning(f"User '{username}' not found")
            raise ValueError("Invalid username or password")
    finally:
        cursor.close()
        connection.close()

def register_new_user(username, password):
    """ 
    Registreer een nieuwe gebruiker
    """
    try:
        db_credentials = get_database_credentials()
        connection = psycopg2.connect(**db_credentials)
        cursor = connection.cursor()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (%s, %s)", (username, hashed_password.decode('utf-8')))
        connection.commit()
        app.logger.info(f"User '{username}' registered successfully")
        return True
    finally:
        cursor.close()
        connection.close()


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
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if register_new_user(username, password):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Failed to register user")
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
