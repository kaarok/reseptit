import sqlite3
import datetime
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import queries
import config

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    for key in list(session.keys()):
        if key.startswith("u_"):
            session.pop(key)

    recipes = queries.get_recipes()
    return render_template("index.html", recipes=recipes)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if len(username) == 0 or len(password1) == 0:
            session["u_invalid_name_password"] = True
            return redirect("/register")
    
    if password1 != password2:
        session["u_password_not_matching"] = True
        return redirect("/register")
    password_hash = generate_password_hash(password1)

    try:
        queries.add_user(username, password_hash)
    except sqlite3.IntegrityError:
        session["u_username_taken"] = True
        return redirect("/register")

    session["username"] = username
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        password_hash = queries.get_password_hash(username)
        if password_hash == []:
            session["u_user_not_found"] = True
            return redirect("/login")
        password_hash = password_hash[0][0]

        if check_password_hash(password_hash, password):
            session["username"] = username
            return redirect("/")
        else:
            session["u_incorrect_password"] = True
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
    ingredients = request.form["ingredients"]
    steps = request.form["steps"]
    created_at = datetime.datetime.now().strftime("%d.%m.%Y")
    user_id = queries.get_user_id(session["username"])
    recipe_id = queries.add_recipe(title, ingredients, steps, created_at, user_id)
    return redirect("/recipe/" + str(recipe_id))

@app.route("/recipe/<int:recipe_id>", methods=["GET"])
def open_recipe(recipe_id):
    recipe = queries.get_recipe(recipe_id)
    ingredients = queries.get_ingredients(recipe_id)
    print(ingredients)
    instructions = queries.get_instructions(recipe_id)
    return render_template("recipe.html", recipe=recipe, ingredients=ingredients, instructions=instructions)

@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = queries.get_recipe(recipe_id)
    if request.method == "GET":
        user_id = queries.get_user_id(session["username"])
        return render_template("edit.html", recipe=recipe, user_id=user_id)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        queries.update_recipe(recipe_id, title, content)
        return redirect("/recipe/" + str(recipe["id"]))

@app.route("/delete/<int:recipe_id>", methods=["GET", "POST"])
def delete_recipe(recipe_id):
    if request.method == "GET":
        recipe = queries.get_recipe(recipe_id)
        return render_template("delete_recipe.html", recipe=recipe)

    if request.method == "POST":
        queries.remove_recipe(recipe_id)
        return redirect("/")

@app.route("/search")
def search():
    query = request.args.get("query")
    results = queries.search(query) if query else []
    return render_template("search.html", query=query, results=results)
