import db
import math

page_size = 10


def add_user(username, password_hash):
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def get_user_id(username):
    sql = "SELECT id FROM users WHERE username = ?"
    return db.query(sql, [username])[0][0]

def get_username(id):
    sql = "SELECT username FROM users WHERE id = ?"
    return db.query(sql, [id])[0][0]

def get_password_hash(username):
    sql = "SELECT password_hash FROM users WHERE username = ?"
    return db.query(sql, [username])

def add_recipe(title, ingredients, instructions, created_at, user_id):
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

    return recipe_id

def get_recipe_count(user_id=None):
    if user_id:
        sql = "SELECT COUNT(id) FROM recipes WHERE user_id = ?"
        return db.query(sql, [user_id])[0][0]
    
    sql = "SELECT COUNT(id) FROM recipes"
    return db.query(sql)[0][0]

def get_page_count(recipe_count=get_recipe_count()):
    page_count = math.ceil(recipe_count / page_size)
    page_count = max(page_count, 1)
    return page_count

def get_page_size():
    return page_size

def get_recipes(page=1, user_id=None):
    limit = page_size
    offset = page_size * (page - 1)

    if user_id:
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
        return db.query(sql, [user_id, limit, offset])
    
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
    return db.query(sql, [limit, offset])

def get_recipe(id):
    sql = """
        SELECT r.id, 
               r.title, 
               ing.ingredient, 
               ins.step, 
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
    return db.query(sql, [id])[0]

def update_recipe(recipe_id, title, ingredients, instructions):
    sql = "UPDATE recipes SET title = ? WHERE id = ?"
    db.execute(sql, [title, recipe_id])

    sql = "DELETE FROM ingredients WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM instructions WHERE recipe_id = ?"
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

    return recipe_id

def remove_recipe(recipe_id):
    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def get_ingredients(recipe_id):
    sql = """
        SELECT i.ingredient
        FROM ingredients i
        WHERE i.recipe_id = ?
        """
    return db.query(sql, [recipe_id])
    

def get_instructions(recipe_id):
    sql = """
        SELECT i.step, i.position
        FROM instructions i
        WHERE i.recipe_id = ?
        ORDER BY i.position"""
    return db.query(sql, [recipe_id])

def add_review(recipe_id, user_id, rating, comment, created_at):
    if rating == None and comment == None:
        return None
    sql = "INSERT INTO reviews (recipe_id, user_id, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [recipe_id, user_id, rating, comment, created_at])

    if rating:
        sql = """
            UPDATE recipes
            SET rating_sum = COALESCE(rating_sum, 0) + ?,
                rating_count = COALESCE(rating_count, 0) + 1
            WHERE id = ?
            """
        db.execute(sql, [rating, recipe_id])


def get_reviews(recipe_id):
    sql = """
        SELECT r.id, r.rating, r.comment, r.created_at, u.username
        FROM reviews r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.recipe_id = ?
        ORDER BY r.created_at DESC
        """
    return db.query(sql, [recipe_id])

def get_user_reviews(user_id):
    sql = """
        SELECT r.id, r.rating, r.comment, r.created_at, u.username
        FROM reviews r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        """
    return db.query(sql, [user_id])

def get_rating(recipe_id):
    sql ="""
        SELECT AVG(rating)
        FROM reviews
        WHERE recipe_id = ?
        """
    rating = db.query(sql, [recipe_id])
    if not rating:
        return rating
    return round(rating[0][0], 1)

def search(query, page):
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
        WHERE r.title LIKE ? OR ing.ingredient LIKE ? OR ins.step LIKE ? OR u.username LIKE ?
        GROUP BY r.id
        ORDER BY
          CASE
            WHEN r.title LIKE ? THEN 0
          ELSE 1
          END,
        r.created_at DESC
        LIMIT ? OFFSET ?
        """
    offset = (page - 1) * page_size
    params = ["%" + query + "%"] * 5 + [page_size, offset]
    return db.query(sql, params)

def search_result_count(query):
    sql = """
        SELECT COUNT(DISTINCT r.id)
        FROM recipes r
          LEFT JOIN users u ON r.user_id = u.id
          LEFT JOIN ingredients ing ON r.id = ing.recipe_id
          LEFT JOIN instructions ins ON r.id = ins.recipe_id
        WHERE r.title LIKE ? OR ing.ingredient LIKE ? OR ins.step LIKE ? OR u.username LIKE ?
        """
    
    params = ["%" + query + "%"] * 4
    count = db.query(sql, params)
    if not count:
        return None
    return count[0][0]
