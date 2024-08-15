import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )

cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@gmail.com', 'password', 'admin')
            )

cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            ('owner', 'owner@gmail.com', 'password', 'owner')
            )

cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            ('worker', 'worker@gmail.com', 'password', 'worker')
            )

connection.commit()
connection.close()
