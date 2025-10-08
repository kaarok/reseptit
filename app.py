from datetime import datetime
from secrets import token_hex

import sqlite3
from flask import Flask, redirect, render_template, flash, abort, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import markupsafe

import queries
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config.from_object(config)

# --------------------
# HOMEPAGE
# --------------------
@app.route("/<int:page>")
@app.route("/")
def index(page: int = 1):
    page_count = queries.get_page_count(queries.get_recipe_count())

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    results = queries.get_recipes(page)
    for r in results:
        r["tags"] = queries.get_tags(r["id"])
    return render_template("index.html", results=results, page=page, page_count=page_count)

@app.route("/search/<int:page>")
@app.route("/search")
def search(page: int = 1):
    query = request.args.get("query")
    if query == "":
        return redirect("/")

    results = queries.get_search_results(query, page)
    for r in results:
        r["tags"] = queries.get_tags(r["id"])
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
    for r in recipes:
        r["tags"] = queries.get_tags(r["id"])
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
        password2="",
        next_page=request.referrer
        )

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    next_page = request.form["next_page"]
    check_user_valid(username, password1)

    error = False
    if password1 != password2:
        flash("*kaksi eri salasanaa annettu")
        error = True

    password_hash = generate_password_hash(password1)

    try:
        queries.add_user(username, password_hash)
    except sqlite3.IntegrityError:
        flash("*käyttäjätunnus on varattu")
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
    session["csrf_token"] = token_hex(16)
    return redirect(next_page)

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if session["username"]:
            return redirect("/")
    except KeyError:
        if request.method == "GET":
            return render_template(
                "login.html",
                username="",
                next_page=request.referrer
                )

    username = request.form["username"]
    password = request.form["password"]
    next_page = request.form["next_page"]

    password_hash = queries.get_password_hash(username)
    if not password_hash:
        flash("*käyttäjänimeä ei löytynyt")
        return render_template(
            "login.html",
            username="",
            next_page=next_page
            )

    if not check_password_hash(password_hash, password):
        flash("*väärä salasana")
        return render_template(
            "login.html",
            username=username,
            next_page=next_page
            )

    session["username"] = username
    session["user_id"] = queries.get_user_id_by_name(username)
    session["csrf_token"] = token_hex(16)
    return redirect(next_page)

@app.route("/logout")
def logout():
    next_page = request.referrer
    try:
        del session["username"]
        del session["user_id"]
        del session["csrf_token"]
        return redirect(next_page)
    except KeyError:
        return redirect(next_page)

# --------------------
# RECIPES
# --------------------
@app.route("/recipe/<int:recipe_id>/<int:page>", methods=["GET"])
@app.route("/recipe/<int:recipe_id>", methods=["GET"])
def show_recipe(recipe_id: int, page: int = 1):
    recipe = queries.get_recipe(recipe_id)
    check_if_found(recipe)
    ingredients = queries.get_ingredients(recipe_id)
    instructions = queries.get_instructions(recipe_id)
    tags = queries.get_tags(recipe_id)
    review_count = queries.get_review_count(recipe_id)

    page_count = queries.get_page_count(review_count)
    if page < 1:
        return redirect("/recipe/" + str(recipe_id))
    if page > page_count:
        return redirect("/recipe/" + str(recipe_id) + "/" + str(page_count))

    reviews = queries.get_reviews(recipe_id, page)

    return render_template(
        "recipe.html",
        recipe=recipe,
        ingredients=ingredients,
        instructions=instructions,
        tags=tags,
        page=page,
        page_count=page_count,
        reviews=reviews,
        review_count=review_count
        )

@app.route("/new_recipe")
def new_recipe():
    require_login()
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
    require_login()
    check_csrf()
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
        check_recipe_valid(title, ingredients, instructions, tags)
        user_id = session["user_id"]
        recipe_id = queries.add_recipe(title, ingredients, instructions, tags, user_id)
        return redirect("/recipe/" + str(recipe_id))

@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id: int):
    form_action = "/edit/" + str(recipe_id)
    recipe = queries.get_recipe(recipe_id)
    check_if_found(recipe)
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

    check_csrf()
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
    check_csrf()
    check_if_found(recipe)
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
    require_login()
    check_csrf()
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
# HELPERS
# --------------------
def require_login():
    if "username" not in session:
        abort(403)

def check_user_id(allowed_id: int):
    if session["user_id"] != allowed_id:
        abort(403)

def check_if_found(item: dict):
    if not item:
        abort(404)

def check_user_valid(username: str, password: str):
    if len(username) < config.USERNAME_LENGTH[0] or len(username) > config.USERNAME_LENGTH[1]:
        abort(403)
    if len(password) < config.PASSWORD_LENGTH[0] or len(password) > config.PASSWORD_LENGTH[1]:
        abort(403)

def check_recipe_valid(
        title: str,
        ingredients: list,
        instructions: list,
        tags: list
        ):
    if len(title) < config.RECIPE_TITLE_LENGTH[0] or len(title) > config.RECIPE_TITLE_LENGTH[1]:
        abort(403)
    for i in ingredients:
        if i == "":
            del i
            continue
        if len(i) < config.INGREDIENT_LENGTH[0] or len(i) > config.INGREDIENT_LENGTH[1]:
            abort(403)
    for i in instructions:
        if i == "":
            del i
            continue
        if len(i) < config.INSTRUCTION_LENGTH[0] or len(i) > config.INSTRUCTION_LENGTH[1]:
            abort(403)
    for i in tags:
        if i == "":
            del i
            continue
        if len(i) < config.TAG_LENGTH[0] or len(i) > config.TAG_LENGTH[1]:
            abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.template_filter("format_date")
def format_date(time: datetime):
    if not time:
        return ""
    time = datetime.fromisoformat(time)
    return time.strftime("%d.%m.%Y")
