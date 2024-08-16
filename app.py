import sqlite3
from flask import Flask, render_template, request, session, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from models.user_model import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['DEBUG'] = True

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def get_db_connection_row():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn


@app.route('/index')
@login_required
def index():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()

    conn = get_db_connection_row()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    app.logger.debug("Route accessed")
    return render_template('index.html', posts=posts)

# -------------------------- CREATE POST --------------------------------


def get_post(post_id):
    conn = get_db_connection_row()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection_row()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection_row()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection_row()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))
# ----------------------------- END CREATE POST ------------------------------------


# ----------------------------- REPORTS ---------------------------------------------
@app.route('/', methods=('GET', 'POST'))
@login_required
def reports():
    conn = get_db_connection_row()
    user_id = session["id"]
    # Fetching the location ID(s) associated with the user
    location_ids = conn.execute(
        'SELECT id FROM locations WHERE location_owner_id = ?', (user_id,)
    ).fetchall()

    # Extract the IDs into a list
    location_ids = [row['id'] for row in location_ids]

    # If there's only one location, use that ID
    if len(location_ids) == 1:
        location_id = location_ids[0]
        reports = conn.execute(
            'SELECT * FROM transactions WHERE location_id = ?', (location_id,)
        ).fetchall()

        # Calculate the grand total for the single location
        grand_total = conn.execute(
            'SELECT SUM(price) FROM transactions WHERE location_id = ?', (location_id,)
        ).fetchone()[0]

    elif len(location_ids) > 1:
        # If there are multiple locations, use an IN clause
        query = 'SELECT * FROM transactions WHERE location_id IN ({})'.format(
            ','.join(['?'] * len(location_ids))
        )
        reports = conn.execute(query, location_ids).fetchall()

        # Calculate the grand total for multiple locations
        grand_total_query = 'SELECT SUM(price) FROM transactions WHERE location_id IN ({})'.format(
            ','.join(['?'] * len(location_ids))
        )
        grand_total = conn.execute(
            grand_total_query, location_ids).fetchone()[0]
    else:
        # No locations found, so reports will be empty
        reports = []
        grand_total = 0  # No data, so total is 0

    conn.close()

    return render_template('reports.html', reports=reports, grand_total=grand_total)


@app.route('/filter_reports', methods=['GET'])
def filter_reports():
    dateFilter = request.args.get('dateFilter')
    locationFilter = request.args.get('locationFilter')
    vehicleFilter = request.args.get('vehicleFilter')

    # The 1=1 in a SQL query is a common technique used to simplify dynamic SQL generation.
    query = 'SELECT * FROM transactions WHERE 1=1'
    params = []

    if dateFilter:
        query += ' AND created = ?'
        params.append(dateFilter)

    if locationFilter:
        query += ' AND location_id = ?'
        params.append(locationFilter)

    if vehicleFilter:
        query += ' AND vehicle_code = ?'
        params.append(vehicleFilter)

    conn = get_db_connection_row()
    reports = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('reports.html', reports=reports)
# ----------------------------- END REPORTS -----------------------------------------


# ----------------------------- MANAGE TICKETS --------------------------------------
@app.route('/manage_tickets', methods=('GET', 'POST'))
@login_required
def manage_tickets():
    return render_template('manage_tickets.html')
# ----------------------------- END MANAGE TICKETS --------------------------------------


# ----------------------------- MANAGE LOCATIONS --------------------------------------
@app.route('/manage_locations', methods=('GET', 'POST'))
@login_required
def manage_locations():
    return render_template('manage_locations.html')


@app.route('/add_location', methods=('GET', 'POST'))
@login_required
def add_location():
    return render_template('add_location.html')
# ----------------------------- END MANAGE LOCATIONS --------------------------------------


# ----------------------------- LOGIN -----------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ? and password = ?',
                    (username, password))
        user = cur.fetchone()
        conn.commit()
        conn.close()
        if user:
            # Get id
            user_id = user[0]
            user_role = user[4]
            user = User(user_id)
            session['id'] = user_id
            session['role'] = user_role
            login_user(user)
            return redirect(url_for('reports'))
        else:
            flash('Invalid username or password!')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ----------------------------- END LOGIN -------------------------------------------------
if __name__ == '__main__':
    app.run()
