import sqlite3
import datetime
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    session["user_not_found"] = False
    session["incorrect_password"] = False
    session["password_not_matching"] = False
    session["username_taken"] = False
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        session["password_not_matching"] = True
        return redirect("/register")
    else:
        session["password_not_matching"] = False
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        session["username_taken"] = True
        return redirect("/register")
    session["username_taken"] = False
    
    session["username"] = username
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT password_hash FROM users WHERE username = ?"
        password_hash = db.query(sql, [username])
        if password_hash == []:
            session["user_not_found"] = True
            return redirect("/login")
        session["user_not_found"] = False
        password_hash = password_hash[0][0]

        if check_password_hash(password_hash, password):
            session["username"] = username
            return redirect("/")
        else:
            session["incorrect_password"] = True
            return redirect("/login")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new_recipe")
def new_recipe():
    return render_template("new_recipe.html")

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    title = request.form["title"]
    content = request.form["content"]
    created_at = datetime.datetime.now()
    sql = "SELECT id FROM users WHERE username = ?"
    user_id = db.query(sql, [session["username"]])[0][0]

    sql = "INSERT INTO recipes (title, content, created_at, user_id) VALUES (?, ?, ?, ?)"
    db.execute(sql, [title, content, created_at, user_id])
    return redirect("/")
