import logging
from flask import Flask, session, redirect, url_for, request, render_template, flash
from functions import register_new_user, authenticate, get_secret, is_authenticated

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route("/")
def index():
    return render_template("index.html", is_authenticated=is_authenticated(session))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if authenticate(username, password, session, app):
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password", "error")
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
        if register_new_user(username, password, app):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Failed to register user")
    return render_template("register.html")

if __name__ == "__main__":
    namespace = "default"
    secret_name = "secret-key-flask"
    app.secret_key = get_secret(namespace, secret_name)
    if app.secret_key: 
        print("Secret fetched successfully")
    else:
        print("Failed to fetch secret.")
    app.run(host="0.0.0.0", port=5000)
