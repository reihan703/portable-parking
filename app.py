from datetime import datetime, timedelta
import hashlib
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


@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Login terlebih dahulu.", "warning")
    return render_template('login.html'), 401


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


# ----------------------------- ADD NEW USER ----------------------------------------
@app.route('/add_new_user', methods=('POST',))
@login_required
def add_new_user():
    conn = get_db_connection()
    user_id = current_user.id
    date_options, location_options, vehicle_options = get_report_options(
        conn=conn, user_id=user_id)
    params = []
    if not session['role'] == 'admin':
        flash("Hanya admin yang bisa menambahkan user baru.", "danger")
        return render_template('reports.html',
                               date_options=date_options,
                               location_options=location_options,
                               vehicle_options=vehicle_options)
    new_username = request.form.get('newUsername')
    new_user_password = request.form.get('newUserPassword')
    new_name = request.form.get('newName')
    new_user_email = request.form.get('newUserEmail')
    new_user_role = request.form.get('newUserRole')
    created_by = session['id']

    # Hash the password
    new_user_password = hashlib.md5(
        new_user_password.encode('utf-8')).hexdigest()
    params.append(new_username)
    params.append(new_user_password)
    params.append(new_name)
    params.append(new_user_email)
    params.append(new_user_role)
    params.append(created_by)

    try:
        query = '''
            INSERT INTO parking_user (username, user_pass, name, email, role, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        conn.execute(query, params)
        conn.commit()
        flash("Pengguna baru berhasil ditambahkan.", "success")
    except Exception as e:
        flash(f"Pengguna baru gagal ditambahkan {e}", "danger")

    conn.close()
    return render_template('reports.html',
                           date_options=date_options,
                           location_options=location_options,
                           vehicle_options=vehicle_options)
# -----------------------------END ADD NEW USER -------------------------------------
# ----------------------------- REPORTS ---------------------------------------------


def get_report_options(conn: sqlite3.Connection, user_id: int):
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

    return date_options, location_options, vehicle_options


@app.route('/', methods=('GET', 'POST'))
@login_required
def reports():
    conn = get_db_connection_row()
    user_id = current_user.id
    reports = []
    total_paid_price = 0

    date_options, location_options, vehicle_options = get_report_options(
        conn=conn, user_id=user_id)

    if request.method == 'POST':
        user_id = current_user.id
        dateFilter = request.form.get('dateFilter')
        locationFilter = request.form.get('locationFilter')
        vehicleFilter = request.form.get('vehicleFilter')
        params = []

        # Get data from database based on filter
        if session['role'] != 'admin':
            query = '''
                SELECT t.*, l.location_name, v.vehicle_code, SUM(t.paid_price) AS total_paid_price
                FROM parking_transaction t 
                JOIN parking_location l ON t.location_id = l.id 
                JOIN parking_vehicle v ON t.vehicle_id = v.id 
                WHERE l.owner_id = ?
            '''
            params.append(user_id)
        else:
            query = '''
                SELECT t.*, l.location_name, v.vehicle_code, SUM(t.paid_price) AS total_paid_price
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

        # Group by to ensure sum calculation is correct
        query += ' GROUP BY t.transaction_id, l.location_name, v.vehicle_code'

        results = conn.execute(query, params).fetchall()
        if results:
            reports = results
            total_paid_price = sum(result['total_paid_price']
                                   for result in results if result['total_paid_price'] is not None)

    conn.close()

    return render_template('reports.html',
                           reports=reports,
                           grand_total=total_paid_price,
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

    try:
        query = '''
            DELETE FROM parking_transaction
            WHERE transaction_id = ?
        '''
        conn.execute(query, (id,))
        conn.commit()
        flash('ID transaksi {} berhasil DIHAPUS'.format(id), "success")
    except:
        flash('ID transaksi {} gagal DIHAPUS'.format(id), "danger")

    conn.close()
    return redirect(url_for('manage_tickets'))


@app.route('/finish_ticket/<string:id>/<int:price>', methods=('GET', 'POST'))
@login_required
def finish_ticket(id, price):
    conn = get_db_connection()

    # Get the current time
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H:%M')
    query = '''
        UPDATE parking_transaction
        SET finished_at = ?, paid_price = ?
        WHERE transaction_id = ?
    '''
    conn.execute(query, (formatted_time, price, id))
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
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

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
    session.clear()
    return redirect(url_for('login'))


@app.route('/forgot_password', methods=('POST',))
def forgot_password():
    username = request.form.get('forgotUsername')
    email = request.form.get('forgotEmail')

    conn = get_db_connection_row()
    query = '''
        SELECT * 
        FROM parking_user
        WHERE username = ?
        AND email = ?
    '''
    user = conn.execute(query, (username, email,)).fetchone()
    if user:
        flash(
            'Data ditemukan, silahkan isi kolom berikut untuk mengubah password', 'success')
        return render_template('forgot_password.html', id=user['id'])
    conn.close()
    flash('Data tidak ditemukan, mohon pastikan email dan username benar', 'warning')
    return render_template('login.html')


@app.route('/reset_password', methods=('POST',))
def reset_password():
    password = request.form.get('resetUserPassword')
    password_check = request.form.get('resetUserPasswordCheck')
    user_id = request.form.get('userId')
    if password != password_check:
        flash('Kata sandi tidak sama, mohon tulis dengan benar!', 'danger')
        return render_template('forgot_password.html', id=user_id)

    # Hash the password
    password = hashlib.md5(
        password.encode('utf-8')).hexdigest()

    conn = get_db_connection()
    query = '''
        UPDATE parking_user
        SET user_pass = ?
        WHERE id = ?
    '''
    conn.execute(query, (password, user_id,))
    conn.commit()
    conn.close()
    flash('Kata sandi berhasil diubah.', 'success')
    return render_template('login.html')

# ----------------------------- END LOGIN -------------------------------------------------


@app.route('/create_transaction', methods=['POST'])
def handle_event():
    data = request.json
    print(f"Received event: {data}")
    # Perform some action based on the event
    if data.get("event"):
        conn = get_db_connection_row()
        transaction_id = data.get('transaction_id')
        location_id = data.get('location_id')
        image_path = data.get('image_path')
        vehicle_code = data.get('vehicle_code')
        status = "Parkir"
        created_at = data.get('created_at')

        # Get vehicle_code
        query = '''
        SELECT pv.id
        FROM parking_vehicle pv
        JOIN parking_location_vehicle plv ON pv.id = plv.vehicle_id
        JOIN parking_location pl ON plv.location_id = pl.id
        WHERE pl.id = ? AND pv.vehicle_code = ?;
        '''
        vehicle_id = conn.execute(
            query, (location_id, vehicle_code,)).fetchone()

        query_insert = '''
        INSERT INTO parking_transaction (transaction_id, location_id, image_path, vehicle_id, status, created_at)
        VALUES (?,?,?,?,?,?)
        '''
        conn.execute(query_insert, (transaction_id, location_id,
                     image_path, vehicle_id, status, created_at,))
        conn.commit()
        conn.close()
        return "Event received", 200

    return "Event Invalid", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
