from datetime import datetime, timedelta
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
    user_id = current_user.id
    reports = []

    # Query the database for options
    now = datetime.now()
    date_options = [(now - timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(14)]

    location_options = conn.execute(
        'SELECT DISTINCT id, location_name FROM locations WHERE location_owner_id = ?', (user_id,)).fetchall()

    vehicle_options = conn.execute(
        """
        SELECT DISTINCT t.vehicle_code 
        FROM transactions t 
        JOIN locations l ON t.location_id = l.id 
        WHERE l.location_owner_id = ?
        """,
        (user_id,)
    ).fetchall()

    if request.method == 'POST':
        user_id = current_user.id
        dateFilter = request.form.get('dateFilter')
        locationFilter = request.form.get('locationFilter')
        vehicleFilter = request.form.get('vehicleFilter')

        query = '''
            SELECT t.*, l.location_name 
            FROM transactions t 
            JOIN locations l ON t.location_id = l.id 
            WHERE l.location_owner_id = ?
        '''
        params = [user_id]

        if dateFilter:
            query += ' AND strftime("%Y-%m-%d", t.created) = ?'
            params.append(dateFilter)

        if locationFilter:
            query += ' AND t.location_id = ?'
            params.append(locationFilter)

        if vehicleFilter:
            query += ' AND t.vehicle_code = ?'
            params.append(vehicleFilter)

        reports = conn.execute(query, params).fetchall()

    conn.close()

    return render_template('reports.html',
                           reports=reports,
                           date_options=date_options,
                           location_options=location_options,
                           vehicle_options=vehicle_options)

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
