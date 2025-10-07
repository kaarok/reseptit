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

USER_COUNT = 100
RECIPE_COUNT = 10**4
REVIEW_COUNT = 10**6
ingredients = [
    "400 g makaroneja",
    "400 g naudan jauhelihaa",
    "1 sipuli",
    "3/4 tl suolaa",
    "3/4 tl mustapippuria",
    "1/4 tl maustepippuria",
    "2 tl basilikaa",
    "2 tl timjamia",
    "2-3 kananmunaa",
    "7 dl kevytmaitoa",
    "1 tl suolaa",
    "2 dl juustoraastetta"
    ]
instructions = [
    "Keitä makaronit pakkauksen ohjeen mukaan, noin 8 minuuttia. Valuta makaronit.",
    "Hienonna sipuli. Ruskista jauheliha omassa rasvassaan ja lisää sipulit jauhelihan joukkoon.",
    "Mausta seos suolalla, musta- ja maustepippurilla, basilikalla sekä timjamilla. Kaada jauhelihaseos ja makaronit isoon voideltuun vuokaan (tilavuus noin 3 l).",
    "Munamaito: Sekoita munamaidon ainekset keskenään ja kaada seos vuokaan.",
    "Kypsennys: Kypsennä 175-asteisessa uunissa noin 45 minuuttia. Ripottele juustoraaste vuoan pinnalle kypsymisen loppuvaiheessa."
    ]
# example recipe source: https://www.k-ruoka.fi/reseptit/liha-makaronilaatikko

tags = [
    "pääruoka",
    "alkuruoka",
    "jälkiruoka",
    "nopea",
    "helppo",
    "kana",
    "gluteeniton",
    "italialainen",
    "vegaaninen",
    "leivonta",
    "pasta"
    ]
for i in tags:
    db.execute(
        "INSERT INTO tags (name) VALUES(?)", [i]
    )

created_at = datetime.datetime.now()


for i in range(1, USER_COUNT + 1):
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ["user" + str(i), generate_password_hash(str(i))]
        )

for recipe in range(1, RECIPE_COUNT + 1):
    db.execute(
        "INSERT INTO recipes (title, created_at, user_id) VALUES (?, ?, ?)",
        ["recipe" + str(recipe), created_at, random.randint(1, USER_COUNT)]
        )

    for i in ingredients:
        if i != "":
            db.execute(
                "INSERT INTO ingredients (recipe_id, ingredient) VALUES (?, ?)",
                [recipe, i]
                )

    POSITION = 0
    for i in instructions:
        if i != "":
            db.execute(
                "INSERT INTO instructions (recipe_id, step, position) VALUES (?, ?, ?)",
                [recipe, i, POSITION]
                )
            POSITION += 1

    tag_ids = random.choices(range(1, len(tags) + 1), k = random.randint(1, 5))
    for i in tag_ids:
        db.execute(
            "INSERT INTO recipe_tags (recipe_id, tag_id) VALUES(?, ?)", [recipe, i]
        )

for i in range(1, REVIEW_COUNT + 1):
    recipe_id = random.randint(1, RECIPE_COUNT)
    rating = random.randint(1, 5)
    db.execute(
        """
        INSERT INTO reviews (recipe_id, user_id, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        [recipe_id, random.randint(1, USER_COUNT), rating, "comment", created_at]
        )

    db.execute(
        """
        UPDATE recipes
        SET rating_sum = COALESCE(rating_sum, 0) + ?,
            rating_count = COALESCE(rating_count, 0) + 1
        WHERE id = ?
        """,
        [rating, recipe_id]
        )

db.commit()
db.close()
