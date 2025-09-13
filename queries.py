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

def add_recipe(title, ingredients, steps, created_at, user_id):
    sql = "INSERT INTO recipes (title, created_at, user_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, created_at, user_id])
    recipe_id = db.last_insert_id()

    ingredients = ingredients.split(", ")
    position = 0
    for i in ingredients:
        i = i.split(" ")
        sql = "INSERT INTO recipe_ingredients (recipe_id, name, amount, unit, position) VALUES (?, ?, ?, ?, ?)"
        db.execute(sql, [recipe_id, i[0], i[1], i[2], position])
        position += 1
    
    steps = steps.split("/")
    position = 0
    for s in steps:
        sql = "INSERT INTO recipe_instructions (recipe_id, step, position) VALUES (?, ?, ?)"
        db.execute(sql, [recipe_id, s, position])

    return recipe_id

def get_recipes():
    sql = """
        SELECT r.id, r.title, r.content, r.created_at, r.user_id, u.username 
        FROM recipes r
          LEFT JOIN users u ON u.id = r.user_id
        ORDER BY r.created_at DESC
        """
    return db.query(sql)

def get_recipe(id):
    sql = """
        SELECT r.id, r.title, r.content, r.created_at, r.user_id, u.username 
        FROM recipes r
          LEFT JOIN users u ON u.id = r.user_id
        WHERE r.id = ?
        """
    return db.query(sql, [id])[0]

def update_recipe(recipe_id, title, content):
    sql = "UPDATE recipes SET content = ?, title = ? WHERE id = ?"
    db.execute(sql, [content, title, recipe_id])

def remove_recipe(recipe_id):
    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])

def get_ingredients(recipe_id):
    sql = """
        SELECT i.name, i.amount, i.unit, i.position
        FROM recipe_ingredients i
        WHERE i.recipe_id = ?
        ORDER BY i.position"""
    return db.query(sql, [recipe_id])
    

def get_instructions(recipe_id):
    sql = """
        SELECT i.step, i.position
        FROM recipe_instructions i
        WHERE i.recipe_id = ?
        ORDER BY i.position"""
    return db.query(sql, [recipe_id])

def search(query):
    sql = """SELECT r.id,
                    r.title,
                    r.content,
                    r.created_at,
                    u.username
             FROM recipes r
              LEFT JOIN users u ON r.user_id = u.id
             WHERE r.title LIKE ? OR r.content LIKE ? OR u.username LIKE ?
             ORDER BY
              CASE
               WHEN r.title LIKE ? THEN 0
               ELSE 1
              END,
              r.created_at DESC"""
    params = ["%" + query + "%"] * 4
    return db.query(sql, params)
