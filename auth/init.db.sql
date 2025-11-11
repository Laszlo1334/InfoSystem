CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

INSERT INTO users (email, password) VALUES ('admin@example.com', 'admin');
INSERT INTO users (email, password) VALUES ('user@example.com', 'user');

