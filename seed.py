# $ python seed.py

import sqlite3
import random
import datetime
from werkzeug.security import generate_password_hash

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM recipes")
db.execute("DELETE FROM ingredients")
db.execute("DELETE FROM instructions")
db.execute("DELETE FROM reviews")
db.execute("DELETE FROM recipe_tags")
db.execute("DELETE FROM tags")

user_count = 1000
recipe_count = 10**5
review_count = 10**6
ingredients = []
instructions = []
created_at = datetime.datetime.now()


for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ["user" + str(i), generate_password_hash(str(i))])

for recipe in range(1, recipe_count + 1):
    db.execute("INSERT INTO recipes (title, created_at, user_id) VALUES (?, ?, ?)", ["recipe" + str(recipe), created_at, random.randint(1, user_count)])

    for i in ingredients:
        if i != "":
            db.execute("INSERT INTO ingredients (recipe_id, ingredient) VALUES (?, ?)", [recipe, i])

    position = 0
    for i in instructions:
        if i != "":
            db.execute("INSERT INTO instructions (recipe_id, step, position) VALUES (?, ?, ?)", [recipe, i, position])
            position += 1

for i in range(1, review_count + 1):
    recipe_id = random.randint(1, recipe_count)
    rating = random.randint(1, 5)
    db.execute("INSERT INTO reviews (recipe_id, user_id, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)", [recipe_id, random.randint(1, user_count), rating, "comment", created_at])

    sql = """
        UPDATE recipes
        SET rating_sum = COALESCE(rating_sum, 0) + ?,
            rating_count = COALESCE(rating_count, 0) + 1
        WHERE id = ?
        """
    db.execute(sql, [rating, recipe_id])

db.commit()
db.close()