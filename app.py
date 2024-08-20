from datetime import datetime, timedelta
import math
import secrets
import sqlite3
import string
from flask import Flask, render_template, request, session, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from core.config import Config
from models.user_model import User

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['FLASK_APP'] = Config.FLASK_APP
app.config['FLASK_ENV'] = Config.FLASK_ENV
app.config['DEBUG'] = Config.FLASK_DEBUG

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def generate_random_key(length=16):
    # Define the characters to use in the key
    characters = string.ascii_letters + string.digits
    # Generate a secure random string
    random_key = ''.join(secrets.choice(characters) for _ in range(length))
    return random_key


def get_db_connection_row():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn


# ----------------------------- REPORTS ---------------------------------------------
@app.route('/', methods=('GET', 'POST'))
@login_required
def reports():
    conn = get_db_connection_row()
    user_id = session["id"]
    user_id = current_user.id
    reports = []

    # Query the database for options
    # Generate date
    now = datetime.now()
    date_options = [(now - timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(14)]

    # Generate location option
    if not session['role'] == 'admin':
        location_query = 'SELECT DISTINCT id, location_name FROM parking_location WHERE owner_id = ?'
        location_options = conn.execute(
            location_query, (user_id,)).fetchall()
    else:
        location_query = 'SELECT DISTINCT id, location_name FROM parking_location'
        location_options = conn.execute(
            location_query).fetchall()

    # Genenaret vehicle option
    if not session['role'] == 'admin':
        vehicle_options = conn.execute(
            """
            SELECT v.vehicle_code, v.vehicle_name, t.vehicle_id 
            FROM parking_transaction t
            JOIN parking_location l ON t.location_id = l.id
            JOIN parking_vehicle v ON t.vehicle_id = v.id
            WHERE l.owner_id = ?
            """,
            (user_id,)
        ).fetchall()
    else:
        vehicle_options = conn.execute(
            """
            SELECT v.vehicle_code, v.vehicle_name, t.vehicle_id 
            FROM parking_transaction t
            JOIN parking_location l ON t.location_id = l.id
            JOIN parking_vehicle v ON t.vehicle_id = v.id
            """
        ).fetchall()

    if request.method == 'POST':
        user_id = current_user.id
        dateFilter = request.form.get('dateFilter')
        locationFilter = request.form.get('locationFilter')
        vehicleFilter = request.form.get('vehicleFilter')
        params = []

        # Get data from databse based on filter
        if not session['role'] == 'admin':
            query = '''
                SELECT t.*, l.location_name, v.vehicle_code 
                FROM parking_transaction t 
                JOIN parking_location l ON t.location_id = l.id 
                JOIN parking_vehicle v ON t.vehicle_id = v.id 
                WHERE l.owner_id = ?
            '''
            params.append(user_id)
        else:
            query = '''
                SELECT t.*, l.location_name, v.vehicle_code 
                FROM parking_transaction t 
                JOIN parking_location l ON t.location_id = l.id 
                JOIN parking_vehicle v ON t.vehicle_id = v.id 
            '''

        if dateFilter:
            query += ' AND strftime("%Y-%m-%d", t.created_at) = ?'
            params.append(dateFilter)

        if locationFilter:
            query += ' AND t.location_id = ?'
            params.append(locationFilter)

        if vehicleFilter:
            query += ' AND t.vehicle_id = ?'
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
def count_price(date_then: str, price: int):
    converted_date = datetime.strptime(date_then, "%Y-%m-%d %H:%M")
    date_now = datetime.now()

    # Calculate the difference in hours
    hours_difference = (date_now - converted_date).total_seconds() / 3600
    hours_difference = math.ceil(hours_difference)
    total_price = hours_difference * price
    return total_price


@app.route('/manage_tickets', methods=('GET', 'POST'))
@login_required
def manage_tickets():
    conn = get_db_connection_row()
    vehicles = ''
    transaction = ''
    price = 0
    ticket = ''
    if request.method == 'POST':
        ticket = request.form.get('ticketInput')
        if not ticket:
            try:
                data = request.get_json()
                ticket = data.get('ticket')
            except:
                pass
         # Query the database to find a matching transaction
        if ticket:
            query = '''
                SELECT t.*, v.vehicle_code, v.vehicle_rate 
                FROM parking_transaction t
                JOIN parking_vehicle v ON t.vehicle_id = v.id
                WHERE t.transaction_id = ?
            '''
            transaction = conn.execute(
                query, (ticket,)).fetchone()

            if not transaction:
                flash("Data transaksi tidak ditemukan.", "warning")
                return render_template('manage_tickets.html', transaction=transaction, price=price)

            price = count_price(
                date_then=transaction['created_at'], price=transaction['vehicle_rate'])
            vehicle_query = '''
                SELECT DISTINCT v.vehicle_code, v.id 
                FROM parking_vehicle v
                JOIN parking_location_vehicle plv ON plv.vehicle_id = v.id
                JOIN parking_transaction pt ON pt.location_id = plv.location_id
                WHERE pt.location_id = ?
            '''
            vehicles = conn.execute(
                vehicle_query, (transaction['location_id'],)).fetchall()
    conn.close()

    return render_template('manage_tickets.html', transaction=transaction, price=price, vehicles=vehicles)


@app.route('/edit_ticket/<string:id>', methods=('GET', 'POST'))
@login_required
def edit_ticket(id):
    vehicle_id = request.form.get('editVehicleCode')
    conn = get_db_connection()
    query = '''
        UPDATE parking_transaction
        SET vehicle_id = ?
        WHERE transaction_id = ?
    '''
    conn.execute(query, (vehicle_id, id))
    conn.commit()
    conn.close()
    flash('Kode kendaraan berhasil diubah!', 'success')
    return redirect(url_for('manage_tickets'))  # Redirect to a relevant page


@app.route('/delete_ticket/<string:id>', methods=('GET', 'POST'))
@login_required
def delete_ticket(id):
    conn = get_db_connection()

    query = '''
        DELETE FROM parking_transaction
        WHERE transaction_id = ?
    '''
    conn.execute(query, (id,))
    conn.commit()
    conn.close()
    flash('ID transaksi {} berhasil DIHAPUS'.format(id), "success")
    return redirect(url_for('manage_tickets'))


@app.route('/finish_ticket/<string:id>', methods=('GET', 'POST'))
@login_required
def finish_ticket(id):
    conn = get_db_connection()

    # Get the current time
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H:%M')
    query = '''
        UPDATE parking_transaction
        SET finished_at = ?
        WHERE transaction_id = ?
    '''
    conn.execute(query, (formatted_time, id))
    conn.commit()
    conn.close()
    flash('ID transaksi {} berhasil DISELESAIKAN'.format(id), "success")
    return redirect(url_for('manage_tickets'))
# ----------------------------- END MANAGE TICKETS --------------------------------------


# ----------------------------- MANAGE LOCATIONS --------------------------------------
def get_locations():
    '''
    Get all available location
    '''
    conn = get_db_connection_row()
    query = '''
    SELECT * FROM parking_location
    '''
    locations = conn.execute(query).fetchall()
    conn.close()
    return locations


def get_owners():
    '''
    Get all available owner
    '''
    conn = get_db_connection_row()
    query = '''
    SELECT * 
    FROM parking_user
    WHERE role = ?
    '''
    owners = conn.execute(query, ('owner',)).fetchall()
    conn.close()
    return owners


@app.route('/manage_locations', methods=('GET', 'POST'))
@login_required
def manage_locations():
    locations = []
    if not session['role'] == 'admin':
        flash("Anda tidak memiliki hak akses", "warning")
        return redirect(url_for('reports'))
    locations = get_locations()
    owners = get_owners()

    return render_template('manage_locations.html', locations=locations, owners=owners)


def get_location(location_id):
    conn = get_db_connection_row()
    query = '''
    SELECT * FROM parking_location WHERE id = ?
    '''
    location = conn.execute(query, (location_id,)).fetchone()
    conn.close()
    if location is None:
        abort(404)
    return location


def get_owner(owner_id):
    conn = get_db_connection_row()
    query = '''
    SELECT * FROM parking_user WHERE id = ?
    '''
    location = conn.execute(query, (owner_id,)).fetchone()
    conn.close()
    if location is None:
        abort(404)
    return location


def get_vehicle(location_id):
    conn = get_db_connection_row()
    query = '''
    SELECT DISTINCT v.vehicle_code, v.id, v.vehicle_rate, v.vehicle_name
    FROM parking_vehicle v
    JOIN parking_location_vehicle plv ON v.id = plv.vehicle_id
    WHERE plv.location_id = ?
    '''
    vehicles = conn.execute(query, (location_id,)).fetchall()
    conn.close()
    if vehicles is None:
        abort(404)
    return vehicles


@app.route('/edit_location/<int:id>/', methods=('GET', 'POST'))
@login_required
def edit_location(id):
    if request.method == "POST":
        location_name = request.form.get('locationName')
        owner_id = request.form.get('ownerId')
        if not location_name or not owner_id:
            flash('Gagal memperbarui data lokasi. Isi semua kolom!', "warning")
        else:
            conn = get_db_connection()
            query = '''
                UPDATE parking_location
                SET location_name = ?, owner_id = ?
                WHERE id = ?
            '''
            conn.execute(query, (location_name, owner_id, id,))
            conn.commit()
            conn.close()
            flash('Lokasi berhasil diperbarui.', "success")
    location = get_location(id)
    owner = get_owner(location['owner_id'])
    owners = get_owners()
    vehicles = get_vehicle(location['id'])
    return render_template('add_location.html', location=location, owner=owner, owners=owners, vehicles=vehicles)


@app.route('/add_location_vehicle_code/<int:id>/', methods=('GET', 'POST'))
@login_required
def add_location_vehicle_code(id):
    location_id = ''
    if request.method == 'POST':
        location_id = request.form['hiddenLocationIdAdd']
        vehicle_code = request.form['addLocationVehicleCode']
        vehicle_name = request.form['addLocationVehicleName']
        vehicle_rate = request.form['addLocationVehicleCodePrice']
        conn = get_db_connection()

        # Insert into the parking_vehicle table
        query_to_parking_vehicle = '''
            INSERT INTO parking_vehicle (vehicle_code, vehicle_name, vehicle_rate)
            VALUES (?, ?, ?)
        '''

        # Execute the query and get the cursor
        cursor = conn.cursor()
        cursor.execute(query_to_parking_vehicle,
                       (vehicle_code, vehicle_name, vehicle_rate))

        # Get the ID of the newly inserted vehicle
        new_vehicle_id = cursor.lastrowid

        # Insert into the parking_location_vehicle table using the new vehicle_id
        query_to_parking_location_vehicle = '''
            INSERT INTO parking_location_vehicle (location_id, vehicle_id)
            VALUES (?, ?)
        '''
        cursor.execute(query_to_parking_location_vehicle,
                       (location_id, new_vehicle_id))

        # Commit the transaction if everything is successful
        conn.commit()
        conn.close()
    return redirect(url_for('edit_location', id=location_id))


@app.route('/edit_location_vehicle_code/<int:id>/', methods=('GET', 'POST'))
@login_required
def edit_location_vehicle_code(id):
    location_id = ''
    if request.method == 'POST':
        location_id = request.form['hiddenLocationId']
        vehicle_code = request.form['editLocationVehicleCode']
        vehicle_rate = request.form['editLocationVehicleCodePrice']
        conn = get_db_connection()
        query = '''
            UPDATE parking_vehicle
            SET vehicle_code = ?, vehicle_rate = ?
            WHERE id = ?
        '''
        conn.execute(query, (vehicle_code, vehicle_rate, id,))
        conn.commit()
        conn.close()
    return redirect(url_for('edit_location', id=location_id))


@app.route('/delete_location_vehicle_code/<int:id>/', methods=('GET', 'POST'))
@login_required
def delete_location_vehicle_code(id):
    conn = get_db_connection()
    query = '''
        DELETE FROM parking_vehicle
        WHERE id = ?
    '''
    conn.execute(query, (id,))
    conn.commit()
    conn.close()
    locations = get_locations()
    owners = get_owners()
    return redirect(url_for('manage_locations', locations=locations, owners=owners))


@app.route('/add_location', methods=('POST',))
@login_required
def add_location():
    if request.method == "POST":
        conn = get_db_connection()
        owner_id = request.form.get('newOwnerName')
        location_name = request.form.get('addNewLocationName')
        admin_id = session['id']
        location_key = generate_random_key(16)
        if not owner_id or not location_name:
            flash("Gagal membuat lokasi baru. Isi semua kolom yang tersedia!", "warning")
        else:
            query = '''
                INSERT INTO parking_location (admin_id, owner_id, location_name, location_key)
                VALUES (?, ?, ?, ?)
            '''

            conn.execute(query, (admin_id, owner_id,
                         location_name, location_key))
            conn.commit()
            conn.close()

        locations = get_locations()
        owners = get_owners()

    return redirect(url_for('manage_locations', locations=locations, owners=owners))
# ----------------------------- END MANAGE LOCATIONS --------------------------------------


# ----------------------------- LOGIN -----------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection_row()
        cur = conn.cursor()
        user_login = cur.execute('SELECT * FROM parking_admin WHERE username = ? and user_pass = ?',
                                 (username, password)).fetchone()
        if not user_login:
            user_login = cur.execute('SELECT * FROM parking_user WHERE username = ? and user_pass = ?',
                                     (username, password)).fetchone()
        conn.commit()
        conn.close()
        if user_login:
            user = User(user_login['id'])
            session['id'] = user_login['id']
            session['role'] = user_login['role']
            session['name'] = user_login['name']
            login_user(user)
            return redirect(url_for('reports'))
        else:
            flash('Invalid username or password!', "danger")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ----------------------------- END LOGIN -------------------------------------------------
if __name__ == '__main__':
    app.run()
