import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Create dummy admin
cur.execute("INSERT INTO parking_admin (username, user_pass, name, email, role) VALUES (?, ?, ?, ?, ?)",
            ('admin', '5f4dcc3b5aa765d61d8327deb882cf99', 'admin lokasi 1', 'admin@gmail.com', 'admin')
            )

# Create dummy owner
cur.execute("INSERT INTO parking_user (username, user_pass, name, email, role, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            ('owner', '5f4dcc3b5aa765d61d8327deb882cf99', 'owner lokasi 1', 'owner@gmail.com', 'owner', 1)
            )
cur.execute("INSERT INTO parking_user (username, user_pass, name, email, role, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            ('owner2', '5f4dcc3b5aa765d61d8327deb882cf99', 'owner lokasi 2', 'owner2@gmail.com', 'owner', 1)
            )

# Create dummy worker
cur.execute("INSERT INTO parking_user (username, user_pass, name, email, role, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            ('worker', '5f4dcc3b5aa765d61d8327deb882cf99', 'worker lokasi 1', 'worker@gmail.com', 'worker', 1)
            )
cur.execute("INSERT INTO parking_user (username, user_pass, name, email, role, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            ('worker2', '5f4dcc3b5aa765d61d8327deb882cf99', 'worker lokasi 2', 'worker2@gmail.com', 'worker', 1)
            )

# Create dummy location
cur.execute("INSERT INTO parking_location (admin_id, owner_id, location_name, location_key) VALUES (?, ?, ?, ?)",
            (1, 1, 'lokasi 1', 'password')
            )
cur.execute("INSERT INTO parking_location (admin_id, owner_id, location_name, location_key) VALUES (?, ?, ?, ?)",
            (1, 2, 'lokasi 2', 'password')
            )

# Create dummy vehicle
cur.execute("INSERT INTO parking_vehicle (vehicle_code, vehicle_name, vehicle_rate) VALUES (?, ?, ?)",
            ('MT1', 'Motor Kecil', 2000)
            )
cur.execute("INSERT INTO parking_vehicle (vehicle_code, vehicle_name, vehicle_rate) VALUES (?, ?, ?)",
            ('MT2', 'Motor Besar', 4000)
            )
cur.execute("INSERT INTO parking_vehicle (vehicle_code, vehicle_name, vehicle_rate) VALUES (?, ?, ?)",
            ('MT3', 'Motor Bebek', 1000)
            )

# Create dummy location_vehicle
cur.execute("INSERT INTO parking_location_vehicle (location_id, vehicle_id) VALUES (?, ?)",
            (1, 1)
            )
cur.execute("INSERT INTO parking_location_vehicle (location_id, vehicle_id) VALUES (?, ?)",
            (1, 2)
            )
cur.execute("INSERT INTO parking_location_vehicle (location_id, vehicle_id) VALUES (?, ?)",
            (2, 3)
            )
cur.execute("INSERT INTO parking_location_vehicle (location_id, vehicle_id) VALUES (?, ?)",
            (2, 2)
            )

# Create dummy transaction
cur.execute("INSERT INTO parking_transaction (transaction_id, location_id, image_path, vehicle_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ('asd', 1, 'sini', 1, 'Parkir', '2024-08-13 21:00')
            )
cur.execute("INSERT INTO parking_transaction (transaction_id, location_id, image_path, vehicle_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ('asdd', 1, 'sini1', 2, 'Keluar', '2024-08-11 21:00')
            )
cur.execute("INSERT INTO parking_transaction (transaction_id, location_id, image_path, vehicle_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ('asds', 2, 'sini2', 3, 'Parkir', '2024-08-19 21:00')
            )
cur.execute("INSERT INTO parking_transaction (transaction_id, location_id, image_path, vehicle_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ('asdss', 2, 'sini3', 2, 'Keluar', '2024-08-17 21:00')
            )

connection.commit()
connection.close()
