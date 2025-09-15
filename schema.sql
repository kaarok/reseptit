CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title TEXT,
    created_at TEXT
);

CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient TEXT
);

CREATE TABLE instructions (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    step TEXT,
    position INTEGER
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    rating INTEGER,
    comment TEXT,
    created_at
);