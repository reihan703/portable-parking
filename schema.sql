DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS vehicles;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role text NOT NULL
);

CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL UNIQUE,
    location_owner_id INTEGER,
    FOREIGN KEY (location_owner_id) REFERENCES users(id)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_code TEXT NOT NULL,
    price INTEGER NOT NULL,
    created TEXT NOT NULL,
    location_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations(id) 
);

CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_code TEXT NOT NULL,
    vehicle_name TEXT NOT NULL,
    price INTEGER NOT NULL,
    location_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations(id) 
);