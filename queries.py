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

def add_recipe(title, content, created_at, user_id):
    sql = "INSERT INTO recipes (title, content, created_at, user_id) VALUES (?, ?, ?, ?)"
    db.execute(sql, [title, content, created_at, user_id])
    return db.last_insert_id()

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