DROP TABLE IF EXISTS parking_raspberry;
DROP TABLE IF EXISTS parking_location;
DROP TABLE IF EXISTS parking_transaction;
DROP TABLE IF EXISTS parking_vehicle;
DROP TABLE IF EXISTS parking_location_vehicle;
DROP TABLE IF EXISTS parking_admin;
DROP TABLE IF EXISTS parking_user;

CREATE TABLE parking_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    user_pass TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE parking_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    user_pass TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE parking_raspberry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raspberry_name TEXT NOT NULL,
    location_id INTEGER NOT NULL,
    FOREIGN KEY (location_id) REFERENCES parking_location(id) ON DELETE CASCADE
);

CREATE TABLE parking_location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    location_name TEXT NOT NULL,
    location_key TEXT NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES parking_admin(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES parking_user(id) ON DELETE CASCADE
);

CREATE TABLE parking_vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_code TEXT NOT NULL,
    vehicle_name TEXT NOT NULL,
    vehicle_rate INTEGER NOT NULL
);

CREATE TABLE parking_location_vehicle (
    location_id INTEGER,
    vehicle_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES parking_location(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES parking_vehicle(id) ON DELETE CASCADE
);

CREATE TABLE parking_transaction (
    transaction_id TEXT PRIMARY KEY NOT NULL,
    raspberry_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    image_path TEXT,
    vehicle_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    finished_at TEXT,
    FOREIGN KEY (raspberry_id) REFERENCES parking_raspberry(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES parking_location(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES parking_vehicle(id) ON DELETE CASCADE
);
