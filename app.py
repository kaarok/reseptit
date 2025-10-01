import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

import datetime
import math

import queries
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/<int:page>")
@app.route("/")
def index(page=1):
    page_count = queries.get_page_count()

    if page < 1:
         return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    for key in list(session.keys()):
        if key.startswith("u_"):
            session.pop(key)

    results = queries.get_recipes(page)
    return render_template("index.html", results=results, page=page, page_count=page_count)

@app.route("/search/<int:page>")
@app.route("/search")
def search(page=1):
    query = request.args.get("query")
    if query == "":
        return redirect("/")
    
    results = queries.search(query, page) if query else []
    result_count = queries.search_result_count(query)
    page_count = queries.get_page_count(result_count)
    
    if page < 1:
         return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    return render_template("index.html", query=query, results=results, page=page, page_count=page_count)

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
    session["user_id"] = queries.get_user_id(username)
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

        if not check_password_hash(password_hash, password):
            session["u_incorrect_password"] = True
            return redirect("/login")
        
        session["username"] = username
        session["user_id"] = queries.get_user_id(username)
        return redirect("/")
            

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new_recipe")
def new_recipe():
    form_action = "/create_recipe"
    ingredients = [""]
    instructions = [""]
    tags = [""]
    all_tags = queries.get_all_tags()

    return render_template("new_recipe.html", form_action=form_action, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    title = request.form.get("title")
    ingredients = request.form.getlist("ingredient")
    instructions = request.form.getlist("instruction")
    tags = request.form.getlist("tags")
    all_tags = queries.get_all_tags()

    if request.form.get("action") == "ingredients_add_row":
        ingredients.append("")
        return render_template("new_recipe.html", title=title, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)
    
    if request.form.get("action") == "instructions_add_row":
        instructions.append("")
        return render_template("new_recipe.html", title=title, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)
    
    if request.form.get("action") == "tags_add_row":
        tags.append("")
        return render_template("new_recipe.html", title=title, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)
    
    if request.form.get("action") == "publish":
        created_at = datetime.datetime.now().strftime("%d.%m.%Y")
        user_id = queries.get_user_id(session["username"])
        recipe_id = queries.add_recipe(title, ingredients, instructions, tags, created_at, user_id)
        return redirect("/recipe/" + str(recipe_id))

@app.route("/recipe/<int:recipe_id>", methods=["GET"])
def show_recipe(recipe_id):
    recipe = queries.get_recipe(recipe_id)
    ingredients = queries.get_ingredients(recipe_id)
    instructions = queries.get_instructions(recipe_id)
    tags = queries.get_tags(recipe_id)
    reviews = queries.get_reviews(recipe_id)
    
    return render_template("recipe.html", recipe=recipe, ingredients=ingredients, instructions=instructions, tags=tags, reviews=reviews)

@app.route("/user/<int:user_id>/<int:page>", methods=["GET"])
@app.route("/user/<int:user_id>", methods=["GET"])
def show_user(user_id, page=1):
    username = queries.get_username(user_id)
    recipes = queries.get_recipes(page, user_id)
    reviews = queries.get_user_reviews(user_id)
    recipe_count = queries.get_recipe_count(user_id)
    activity = {"recipe_count": recipe_count, "review_count": len(reviews)}

    page_count = queries.get_page_count(recipe_count)
    if page < 1:
         return redirect("/user/" + str(user_id))
    if page > page_count:
        return redirect("/user/" + str(user_id) + "/" + str(page_count))
    
    return render_template("user.html", user_id=user_id, username=username, user_recipes=recipes, user_reviews=reviews, activity=activity, page=page, page_count=page_count)

@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    form_action = "/edit/" + str(recipe_id)
    recipe = queries.get_recipe(recipe_id)
    all_tags = queries.get_all_tags()

    if request.method == "GET":
        title = recipe["title"]
        ingredients = [r["ingredient"] for r in queries.get_ingredients(recipe_id)]
        instructions = [r["step"] for r in queries.get_instructions(recipe_id)]
        tags = [r["name"] for r in queries.get_tags(recipe_id)]
        return render_template("edit.html", form_action=form_action, recipe=recipe, title=title, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)

    title = request.form.get("title")
    ingredients = request.form.getlist("ingredient")
    instructions = request.form.getlist("instruction")
    tags = request.form.getlist("tags")
    
    if request.form.get("action") == "ingredients_add_row":
        ingredients.append("")
        return render_template("edit.html", recipe=recipe, title=title, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)
    
    if request.form.get("action") == "instructions_add_row":
        instructions.append("")
        return render_template("edit.html", recipe=recipe, title=title, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)
    
    if request.form.get("action") == "tags_add_row":
        tags.append("")
        return render_template("new_recipe.html", title=title, ingredients=ingredients, instructions=instructions, tags=tags, all_tags=all_tags)
    
    
    if request.form.get("action") == "publish":
        recipe_id = queries.update_recipe(recipe_id, title, ingredients, instructions, tags=tags)
        return redirect("/recipe/" + str(recipe_id))

@app.route("/delete/<int:recipe_id>", methods=["GET", "POST"])
def delete_recipe(recipe_id):
    if request.method == "GET":
        recipe = queries.get_recipe(recipe_id)
        return render_template("delete_recipe.html", recipe=recipe)

    if request.method == "POST":
        queries.remove_recipe(recipe_id)
        return redirect("/")
    
@app.route("/create_review/<int:recipe_id>", methods=["POST"])
def create_review(recipe_id):
    rating = request.form["rating"]
    comment = request.form["comment"].strip()
    if rating == "" and comment == "":
        return redirect("/recipe/" + str(recipe_id))
    
    user_id =   queries.get_user_id(session["username"])
    created_at = datetime.datetime.now().strftime("%d.%m.%Y")
    queries.add_review(recipe_id, user_id, rating, comment, created_at)
    return redirect("/recipe/" + str(recipe_id))
