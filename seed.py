# $ python seed.py

import random
from app import app
import queries
import db
from werkzeug.security import generate_password_hash


def seed():
    db.execute("DELETE FROM users")
    db.execute("DELETE FROM recipes")
    db.execute("DELETE FROM ingredients")
    db.execute("DELETE FROM instructions")
    db.execute("DELETE FROM reviews")

    user_count = 100
    recipe_count = 10**3
    review_count = 10**3

    for i in range(1, user_count + 1):
        queries.add_user("user" + str(i), generate_password_hash(str(i)))

    for i in range(1, recipe_count + 1):
        queries.add_recipe("recipe" + str(i), [], [], 0, random.randint(1, user_count))

    for i in range(1, review_count + 1):
        queries.add_review(random.randint(1, recipe_count), random.randint(1, user_count), random.randint(1, 5), "comment", 0)

if __name__ == "__main__":
    with app.app_context():
        seed()