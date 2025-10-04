import math
from datetime import datetime

import config
import db


# --------------------
# USERS
# --------------------
def add_user(username: str, password_hash: str) -> None:
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def get_user_id_by_name(username: str) -> int:
    sql = "SELECT id FROM users WHERE username = ?"
    return db.query(sql, [username])[0][0]

def get_username_by_id(idx: int) -> str:
    sql = "SELECT username FROM users WHERE id = ?"
    return db.query(sql, [idx])[0][0]

def get_password_hash(username: str) -> str:
    sql = "SELECT password_hash FROM users WHERE username = ?"
    return db.query(sql, [username])[0][0]

# --------------------
# RECIPES
# --------------------
def add_recipe(title: str, ingredients: list, instructions: list, tags: list, user_id: int) -> int:
    created_at = datetime.now()
    sql = "INSERT INTO recipes (title, created_at, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, created_at, user_id])
    recipe_id = db.last_insert_id()

    sql = "INSERT INTO ingredients (recipe_id, ingredient) VALUES (?, ?)"
    for i in ingredients:
        if i != "":
            db.execute(sql, [recipe_id, i])

    sql = "INSERT INTO instructions (recipe_id, step, position) VALUES (?, ?, ?)"
    position = 0
    for i in instructions:
        if i != "":
            db.execute(sql, [recipe_id, i, position])
            position += 1

    for tag in tags:
        if tag != "":
            tag = tag.strip().lower()
            db.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", [tag])
            tag_id = db.query("SELECT id FROM tags WHERE name = ?", [tag])[0]["id"]
            db.execute(
                "INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)",
                [recipe_id, tag_id]
                )

    return recipe_id

def update_recipe(
        recipe_id: int,
        title: str,
        ingredients: list,
        instructions: list,
        tags: list
        ) -> int:
    sql = "UPDATE recipes SET title = ? WHERE id = ?"
    db.execute(sql, [title, recipe_id])

    sql = "DELETE FROM ingredients WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM instructions WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM recipe_tags WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])

    sql = "INSERT INTO ingredients (recipe_id, ingredient) VALUES (?, ?)"
    for i in ingredients:
        if i != "":
            db.execute(sql, [recipe_id, i])

    sql = "INSERT INTO instructions (recipe_id, step, position) VALUES (?, ?, ?)"
    position = 0
    for i in instructions:
        if i != "":
            db.execute(sql, [recipe_id, i, position])
            position += 1

    for tag in tags:
        if tag != "":
            tag = tag.strip().lower()
            db.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", [tag])
            tag_id = db.query("SELECT id FROM tags WHERE name = ?", [tag])[0]["id"]
            db.execute(
                "INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)",
                [recipe_id, tag_id]
                )

    return recipe_id

def remove_recipe(recipe_id: int) -> None:
    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def get_recipe_count(user_id: int = None) -> int:
    if user_id:
        sql = "SELECT COUNT(id) FROM recipes WHERE user_id = ?"
        return db.query(sql, [user_id])[0][0]

    sql = "SELECT COUNT(id) FROM recipes"
    return db.query(sql)[0][0]

def get_recipes(page: int = 1) -> list[dict]:
    limit = config.PAGE_SIZE
    offset = limit * (page - 1)
    sql = """
        SELECT r.id,
               r.title,
               r.user_id,
               r.created_at,
               u.username,
               r.rating_sum,
               r.rating_count,
               CASE
                   WHEN r.rating_count > 0 THEN ROUND(r.rating_sum * 1.0 / r.rating_count, 1)
                   ELSE NULL
               END AS avg_rating
        FROM recipes r
            LEFT JOIN users u ON u.id = r.user_id
        ORDER BY r.created_at DESC
        LIMIT ? OFFSET ?
        """
    result = db.query(sql, [limit, offset])
    return sql_rows_to_dicts(result)

def get_user_recipes(user_id: int, page: int = 1) -> list[dict]:
    limit = config.PAGE_SIZE
    offset = limit * (page - 1)
    sql = """
        SELECT r.id,
        r.title,
        r.user_id,
        r.created_at,
        u.username,
        r.rating_sum,
        r.rating_count,
        CASE
            WHEN r.rating_count > 0 THEN r.rating_sum * 1.0 / r.rating_count
            ELSE NULL
        END AS avg_rating
        FROM recipes r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        LIMIT ? OFFSET ?
        """
    result = db.query(sql, [user_id, limit, offset])
    return sql_rows_to_dicts(result)

def get_recipe(idx: int) -> dict:
    sql = """
        SELECT r.id, 
               r.title, 
               r.created_at, 
               r.user_id,
               u.username,
               r.rating_sum,
               r.rating_count,
               CASE
                   WHEN r.rating_count > 0 THEN ROUND(r.rating_sum * 1.0 / r.rating_count, 1)
                   ELSE NULL
               END AS avg_rating
        FROM recipes r
          LEFT JOIN users u ON u.id = r.user_id
          LEFT JOIN ingredients ing ON ing.recipe_id = r.id
          LEFT JOIN instructions ins ON ins.recipe_id = r.id
        WHERE r.id = ?
        """
    result = db.query(sql, [idx])
    return sql_rows_to_dicts(result)[0]

# --------------------
# INGREDIENTS
# --------------------
def get_ingredients(recipe_id: int) -> list[str]:
    sql = """
        SELECT i.ingredient
        FROM ingredients i
        WHERE i.recipe_id = ?
        """
    result = db.query(sql, [recipe_id])
    return sql_col_to_list(result, "ingredient")

# --------------------
# INSTRUCTIONS
# --------------------
def get_instructions(recipe_id: int) -> list[str]:
    sql = """
        SELECT i.step, i.position
        FROM instructions i
        WHERE i.recipe_id = ?
        ORDER BY i.position
        """
    result = db.query(sql, [recipe_id])
    return sql_col_to_list(result, "step")

# --------------------
# TAGS
# --------------------
def get_tags(recipe_id: int) -> list[str]:
    sql = """
        SELECT t.name
        FROM recipe_tags rt
          LEFT JOIN tags t ON t.id = rt.tag_id
        WHERE rt.recipe_id = ?
        """
    result = db.query(sql, [recipe_id])
    return sql_col_to_list(result, "name")

def get_all_tags() -> list[str]:
    sql = "SELECT name FROM tags"
    result = db.query(sql)
    if not result:
        return None
    return sql_col_to_list(result, "name")

# --------------------
# REVIEWS
# --------------------
def add_review(recipe_id: int, user_id: int, rating: str, comment: str) -> None:
    if rating is None and comment is None:
        return
    created_at = datetime.now()
    sql = """
        INSERT INTO reviews (recipe_id, user_id, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
    db.execute(sql, [recipe_id, user_id, rating, comment, created_at])

    if rating:
        sql = """
            UPDATE recipes
            SET rating_sum = COALESCE(rating_sum, 0) + ?,
                rating_count = COALESCE(rating_count, 0) + 1
            WHERE id = ?
            """
        db.execute(sql, [rating, recipe_id])

def get_reviews(recipe_id: int) -> list[dict]:
    sql = """
        SELECT r.id, r.rating, r.comment, r.created_at, r.user_id, u.username
        FROM reviews r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.recipe_id = ?
        ORDER BY r.created_at DESC
        """
    result = db.query(sql, [recipe_id])
    return sql_rows_to_dicts(result)

def get_user_reviews(user_id: int) -> list[dict]:
    sql = """
        SELECT r.id, r.rating, r.comment, r.created_at, r.user_id, u.username
        FROM reviews r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        """
    result = db.query(sql, [user_id])
    return sql_rows_to_dicts(result)

# --------------------
# SEARCH
# --------------------
def get_search_results(query: str, page: int) -> list[dict]:
    sql = """
        SELECT r.id,
               r.title,
               r.user_id,
               r.created_at,
               u.username,
               r.rating_sum,
               r.rating_count,
               CASE
                 WHEN r.rating_count > 0 THEN ROUND(r.rating_sum * 1.0 / r.rating_count, 1)
                 ELSE NULL
               END AS avg_rating
        FROM recipes r
          LEFT JOIN users u ON r.user_id = u.id
          LEFT JOIN ingredients ing ON r.id = ing.recipe_id
          LEFT JOIN instructions ins ON r.id = ins.recipe_id
          LEFT JOIN recipe_tags rt ON r.id = rt.recipe_id
          LEFT JOIN tags t ON t.id = rt.tag_id
        WHERE r.title LIKE ? OR ing.ingredient LIKE ? OR ins.step LIKE ? OR u.username LIKE ? OR t.name LIKE ?
        GROUP BY r.id
        ORDER BY
          CASE
            WHEN r.title LIKE ? THEN 0
          ELSE 1
          END,
        r.created_at DESC
        LIMIT ? OFFSET ?
        """
    offset = (page - 1) * config.PAGE_SIZE
    params = ["%" + query + "%"] * 6 + [config.PAGE_SIZE, offset]
    result = db.query(sql, params)
    return sql_rows_to_dicts(result)

def get_search_result_count(query: str) -> int:
    sql = """
        SELECT COUNT(DISTINCT r.id)
        FROM recipes r
          LEFT JOIN users u ON r.user_id = u.id
          LEFT JOIN ingredients ing ON r.id = ing.recipe_id
          LEFT JOIN instructions ins ON r.id = ins.recipe_id
          LEFT JOIN recipe_tags rt ON r.id = rt.recipe_id
          LEFT JOIN tags t ON t.id = rt.tag_id
        WHERE r.title LIKE ? OR ing.ingredient LIKE ? OR ins.step LIKE ? OR u.username LIKE ? OR t.name LIKE ?
        """

    params = ["%" + query + "%"] * 5
    count = db.query(sql, params)
    if not count:
        return None
    return count[0][0]

# --------------------
# HELPER
# --------------------
def get_page_count(recipe_count: int = get_recipe_count()) -> int:
    page_count = math.ceil(recipe_count / config.PAGE_SIZE)
    page_count = max(page_count, 1)
    return page_count

def sql_rows_to_dicts(sql_rows: list) -> list[dict]:
    return [dict(row) for row in sql_rows]

def sql_col_to_list(sql_rows: list, col_name: str) -> list:
    return [row[col_name] for row in sql_rows]
