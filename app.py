from datetime import datetime

import sqlite3
from flask import Flask, redirect, render_template, flash, abort, request, session
from werkzeug.security import generate_password_hash, check_password_hash

import queries
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# --------------------
# HOMEPAGE
# --------------------
@app.route("/<int:page>")
@app.route("/")
def index(page: int = 1):
    page_count = queries.get_page_count()

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    results = queries.get_recipes(page)
    return render_template("index.html", results=results, page=page, page_count=page_count)

@app.route("/search/<int:page>")
@app.route("/search")
def search(page: int = 1):
    query = request.args.get("query")
    if query == "":
        return redirect("/")

    results = queries.get_search_results(query, page) if query else []
    result_count = queries.get_search_result_count(query)
    page_count = queries.get_page_count(result_count)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    return render_template(
        "index.html",
        query=query,
        results=results,
        page=page,
        page_count=page_count
        )

# --------------------
# USERS
# --------------------
@app.route("/user/<int:user_id>/<int:page>", methods=["GET"])
@app.route("/user/<int:user_id>", methods=["GET"])
def show_user(user_id: int, page: int = 1):
    username = queries.get_username_by_id(user_id)
    recipes = queries.get_user_recipes(user_id, page)
    reviews = queries.get_user_reviews(user_id)
    recipe_count = queries.get_recipe_count(user_id)
    activity = {"recipe_count": recipe_count, "review_count": len(reviews)}

    page_count = queries.get_page_count(recipe_count)
    if page < 1:
        return redirect("/user/" + str(user_id))
    if page > page_count:
        return redirect("/user/" + str(user_id) + "/" + str(page_count))

    return render_template(
        "user.html",
        user_id=user_id,
        username=username,
        user_recipes=recipes,
        user_reviews=reviews,
        activity=activity,
        page=page,
        page_count=page_count
        )

@app.route("/register")
def register():
    return render_template(
        "register.html",
        username="",
        password1="",
        password2=""
        )

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    error = False
    if len(username) == 0:
        flash("*käyttäjänimi on pakollinen")
        error = True
    if len(password1) == 0:
        flash("*salasana on pakollinen")
        error = True

    if password1 != password2:
        flash("*kaksi eri salasanaa annettu")
        error = True

    password_hash = generate_password_hash(password1)

    try:
        queries.add_user(username, password_hash)
    except sqlite3.IntegrityError:
        flash("*käyttäjänimi on varattu")
        error = True

    if error:
        return render_template(
            "register.html",
            username=username,
            password1=password1,
            password2=password2
            )

    session["username"] = username
    session["user_id"] = queries.get_user_id_by_name(username)
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session["username"]:
        return redirect("/")
    if request.method == "GET":
        return render_template(
            "login.html",
            username=""
            )

    username = request.form["username"]
    password = request.form["password"]

    password_hash = queries.get_password_hash(username)
    if not password_hash:
        flash("*käyttäjänimeä ei löytynyt")
        return render_template(
            "login.html",
            username=""
            )

    if not check_password_hash(password_hash, password):
        flash("*väärä salasana")
        return render_template(
            "login.html",
            username=username
            )

    session["username"] = username
    session["user_id"] = queries.get_user_id_by_name(username)
    return redirect("/")

@app.route("/logout")
def logout():
    if session["username"]:
        del session["username"]
    return redirect("/")

# --------------------
# RECIPES
# --------------------
@app.route("/recipe/<int:recipe_id>", methods=["GET"])
def show_recipe(recipe_id: int):
    recipe = queries.get_recipe(recipe_id)
    check_recipe(recipe)
    ingredients = queries.get_ingredients(recipe_id)
    instructions = queries.get_instructions(recipe_id)
    tags = queries.get_tags(recipe_id)
    reviews = queries.get_reviews(recipe_id)

    return render_template(
        "recipe.html",
        recipe=recipe,
        ingredients=ingredients,
        instructions=instructions,
        tags=tags,
        reviews=reviews
        )

@app.route("/new_recipe")
def new_recipe():
    form_action = "/create_recipe"
    ingredients = [""]
    instructions = [""]
    tags = [""]
    all_tags = queries.get_all_tags()

    return render_template(
        "new_recipe.html",
        form_action=form_action,
        ingredients=ingredients,
        instructions=instructions,
        tags=tags,
        all_tags=all_tags
        )

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    title = request.form.get("title")
    ingredients = request.form.getlist("ingredient")
    instructions = request.form.getlist("instruction")
    tags = request.form.getlist("tags")
    all_tags = queries.get_all_tags()

    if request.form.get("action") == "ingredients_add_row":
        ingredients.append("")
        return render_template(
            "new_recipe.html",
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

    if request.form.get("action") == "instructions_add_row":
        instructions.append("")
        return render_template(
            "new_recipe.html",
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

    if request.form.get("action") == "tags_add_row":
        tags.append("")
        return render_template(
            "new_recipe.html",
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

    if request.form.get("action") == "publish":
        if title.strip() == "":
            flash("*reseptin nimi on pakollinen")
            return render_template(
                "new_recipe.html",
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                tags=tags,
                all_tags=all_tags
                )
        user_id = queries.get_user_id_by_name(session["username"])
        recipe_id = queries.add_recipe(title, ingredients, instructions, tags, user_id)
        return redirect("/recipe/" + str(recipe_id))

    return render_template(
            "new_recipe.html",
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id: int):
    form_action = "/edit/" + str(recipe_id)
    recipe = queries.get_recipe(recipe_id)
    check_recipe(recipe)
    check_user_id(recipe["user_id"])
    all_tags = queries.get_all_tags()

    if request.method == "GET":
        title = recipe["title"]
        ingredients = queries.get_ingredients(recipe_id)
        instructions = queries.get_instructions(recipe_id)
        tags = queries.get_tags(recipe_id)
        return render_template(
            "edit.html",
            form_action=form_action,
            recipe=recipe,
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

    title = request.form.get("title")
    ingredients = request.form.getlist("ingredient")
    instructions = request.form.getlist("instruction")
    tags = request.form.getlist("tags")

    if request.form.get("action") == "ingredients_add_row":
        ingredients.append("")
        return render_template(
            "edit.html",
            recipe=recipe,
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

    if request.form.get("action") == "instructions_add_row":
        instructions.append("")
        return render_template(
            "edit.html",
            recipe=recipe,
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

    if request.form.get("action") == "tags_add_row":
        tags.append("")
        return render_template(
            "edit.html",
            recipe=recipe,
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

    if request.form.get("action") == "publish":
        recipe_id = queries.update_recipe(recipe_id, title, ingredients, instructions, tags=tags)
        return redirect("/recipe/" + str(recipe_id))

    return render_template(
            "edit.html",
            recipe=recipe,
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            tags=tags,
            all_tags=all_tags
            )

@app.route("/delete/<int:recipe_id>", methods=["GET", "POST"])
def delete_recipe(recipe_id: int):
    recipe = queries.get_recipe(recipe_id)
    check_recipe(recipe)
    check_user_id(recipe["user_id"])
    if request.method == "GET":
        return render_template("delete_recipe.html", recipe=recipe)

    queries.remove_recipe(recipe_id)
    return redirect("/")

# --------------------
# REVIEWS
# --------------------
@app.route("/create_review/<int:recipe_id>", methods=["POST"])
def create_review(recipe_id: int):
    rating = request.form["rating"]
    print(type(rating))
    comment = request.form["comment"].strip()
    if rating == "" and comment == "":
        flash("*arvostelulla täytyy olla arvosana tai kommentti")
        return redirect("/recipe/" + str(recipe_id))

    user_id =   queries.get_user_id_by_name(session["username"])
    queries.add_review(recipe_id, user_id, rating, comment)
    return redirect("/recipe/" + str(recipe_id))

# --------------------
# HELPER
# --------------------
def check_user_id(allowed_id):
    if session["user_id"] != allowed_id:
        abort(403)

def check_recipe(recipe):
    if not recipe:
        abort(404)

@app.template_filter("format_date")
def format_date(time: datetime):
    if not time:
        return ""
    time = datetime.fromisoformat(time)
    return time.strftime("%d.%m.%Y")
