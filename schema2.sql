DROP TABLE IF EXISTS raspberry;
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS transaction;
DROP TABLE IF EXISTS vehicle;
DROP TABLE IF EXISTS location_vehicle;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    user_pass TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role text NOT NULL
);

CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    user_pass TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role text NOT NULL
);

CREATE TABLE raspberry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raspberry_name TEXT NOT NULL,
    location_id TEXT NOT NULL,
    FOREIGN KEY (location_id) REFERENCES location(id)
);

CREATE TABLE location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INT NOT NULL,
    owner_id INT NOT NULL,
    location_name TEXT NOT NULL,
    location_key TEXT NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES admin(id),
    FOREIGN KEY (owner_id) REFERENCES user(id),
);

CREATE TABLE vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_code TEXT NOT NULL,
    vehicle_name TEXT NOT NULL,
    vehicle_rate INT NOT NULL,
);

CREATE TABLE location_vehicle (
    location_id INTEGER PRIMARY KEY,
    vehicle_id INTEGER PRIMARY KEY,
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(id),
);

CREATE TABLE transaction (
    transaction_id TEXT PRIMARY KEY NOT NULL,
    raspberry_id INT NOT NULL,
    location_id INT NOT NULL,
    image_path TEXT,
    price INT,
    vehicle_code TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (raspberry_id) REFERENCES raspberry(id),
    FOREIGN KEY (location_id) REFERENCES location(id),
)


