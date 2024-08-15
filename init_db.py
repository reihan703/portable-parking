import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Testing
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )

# Create dummy user
cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@gmail.com', 'password', 'admin')
            )

cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            ('owner', 'owner@gmail.com', 'password', 'owner')
            )

cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            ('worker', 'worker@gmail.com', 'password', 'worker')
            )

# Create dummy locations
cur.execute("INSERT INTO locations (location_name, location_owner_id) VALUES (?, ?)",
            ('testing', '2')
            )

# Create dummy transactions
cur.execute("INSERT INTO transactions (vehicle_code, price, created, location_id) VALUES (?, ?, ?, ?)",
            ('MT1', '2000', '2024-8-15 21:00', '1')
            )



connection.commit()
connection.close()
