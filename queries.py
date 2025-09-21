import db

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

def get_recipes(user_id=None):
    if user_id:
        sql = """
        SELECT r.id, r.title, r.user_id, r.created_at, u.username
        FROM recipes r
          LEFT JOIN users u ON u.id = r.user_id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        """
        return db.query(sql, [user_id])
    
    sql = """
        SELECT r.id, r.title, r.user_id, r.created_at, u.username
        FROM recipes r
          LEFT JOIN users u ON u.id = r.user_id
        ORDER BY r.created_at DESC
        """
    return db.query(sql)

def get_recipe(id):
    sql = """
        SELECT r.id, r.title, ing.ingredient, ins.step, r.created_at, r.user_id, u.username 
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

def get_reviews(recipe_id):
    sql = """SELECT r.id, r.rating, r.comment, r.created_at, u.username
             FROM reviews r
               LEFT JOIN users u ON u.id = r.user_id
             WHERE r.recipe_id = ?
             ORDER BY r.created_at DESC
            """
    return db.query(sql, [recipe_id])

def search(query):
    sql = """SELECT r.id,
                    r.title,
                    r.created_at,
                    u.username
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
              r.created_at DESC"""
    params = ["%" + query + "%"] * 5
    return db.query(sql, params)
