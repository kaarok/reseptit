CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE recipes (
    id integer PRIMARY KEY,
    title TEXT,
    content TEXT,
    created_at TEXT,
    user_id INTEGER REFERENCES users
);