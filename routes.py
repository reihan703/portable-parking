from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from middleware import auth
from models.user_model import User

bp = Blueprint('main', __name__)


@bp.route('/')
@auth
def index():
    return render_template('reports.html',)

# ----------------------------- REPORTS ---------------------------------------------

@bp.route('/reports', methods=('GET', 'POST'))
@auth
def reports():
    return render_template('reports.html')
# ----------------------------- END REPORTS -----------------------------------------

# ----------------------------- MANAGE TICKETS --------------------------------------

@bp.route('/manage_tickets', methods=('GET', 'POST'))
@auth
def manage_tickets():
    return render_template('manage_tickets.html')
# ----------------------------- END MANAGE TICKETS --------------------------------------

# ----------------------------- MANAGE LOCATIONS --------------------------------------

@bp.route('/manage_locations', methods=('GET', 'POST'))
@auth
def manage_locations():
    return render_template('manage_locations.html')

@bp.route('/add_location', methods=('GET', 'POST'))
@auth
def add_location():
    return render_template('add_location.html')
# ----------------------------- END MANAGE LOCATIONS --------------------------------------

# ----------------------------- LOGIN -----------------------------------------------------
# @bp.route('/login', methods=('GET', 'POST'))
# def login():
#     return render_template('login.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch the user from the database
        user = User.query.filter_by(username=username).first()

        # Check if user exists and the password matches
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@bp.route('/logout')
@auth
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('logged_in', False)  # Remove logged in from session
    return redirect(url_for('login'))
