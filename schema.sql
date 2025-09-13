CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    created_at TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFRENCES recipes,
    name TEXT,
    amount TEXT,
    unit TEXT,
    position INTEGER
);

CREATE TABLE recipe_instructions (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFRENCES recipes,
    step TEXT,
    position INTEGER
);