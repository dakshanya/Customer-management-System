from flask import Flask, render_template, request, redirect, url_for, flash, jsonify 
import sqlite3
import os
from datetime import datetime, timedelta
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)
app.secret_key = '12345678abcd'
print(datetime.now())
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'dakshanyasv@gmail.com'
EMAIL_PASSWORD = 'dvfaixxeixfcoezj'
otp_storage = {}  # Store email-otp pairs temporarily

# Database initialization
def init_db():
    if not os.path.exists('databasewithcustomer.db'):
        conn = sqlite3.connect('databasewithcustomer.db')
        c = conn.cursor()

        # User table
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        # Customers table
        c.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                product TEXT NOT NULL,
                status TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                warrantyYears TEXT NOT NULL,
                avatar TEXT
            )
        ''')
        

        conn.commit()
        conn.close()

# Route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        try:
            conn = sqlite3.connect('databasewithcustomer.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)",
                      (full_name, email, password, role))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Email already registered. Try a different one.")
            return redirect(url_for('register'))
        except sqlite3.OperationalError:
            flash("Database is locked. Try again shortly.")
            return redirect(url_for('register'))
        finally:
            conn.close() 

        flash("Account created successfully! Please login.")
        return redirect(url_for('signin'))

    return render_template('register.html')


# Route login page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = sqlite3.connect('databasewithcustomer.db')
            c = conn.cursor()
            c.execute("SELECT role FROM users WHERE email = ? AND password = ?", (email, password))
            user = c.fetchone()
        finally:
            conn.close()

        if user:
            if user[0].lower() == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return "Logged in as " + user[0].capitalize()
        else:
            flash("Invalid credentials")
            return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        conn = sqlite3.connect('databasewithcustomer.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user:
            otp = str(random.randint(100000, 999999))
            otp_storage[email] = otp

            try:
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = email
                msg['Subject'] = 'Your OTP for Password Reset'
                body = f'Your OTP is: {otp}'
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()

                flash('OTP sent to your email.')
                return redirect(url_for('verify_otp', email=email))
            except Exception as e:
                flash('Failed to send email. Try again later.')
                print(e)
                return redirect(url_for('forgot_password'))
        else:
            flash('Email not found.')
            return redirect(url_for('forgot_password'))

    return render_template('forgot-password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        email = request.form['email']
        entered_otp = request.form['otp']
        actual_otp = otp_storage.get(email)

        if actual_otp == entered_otp:
            return redirect(url_for('reset_password', email=email))
        else:
            flash('Invalid OTP. Try again.')
            return redirect(url_for('verify_otp', email=email))

    # GET method
    email = request.args.get('email')
    return render_template('otp-verification.html', email=email)


@app.route('/resend-otp')
def resend_otp():
    email = request.args.get('email')

    if email:
        otp = str(random.randint(100000, 999999))
        otp_storage[email] = otp

        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = email
            msg['Subject'] = 'Your OTP (Resent)'
            body = f'Your new OTP is: {otp}'
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            flash('OTP resent successfully.')
        except Exception as e:
            print(e)
            flash('Failed to resend OTP. Try again.')

    return redirect(url_for('verify_otp', email=email))


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('reset_password', email=email))

        conn = sqlite3.connect('databasewithcustomer.db')
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
        conn.close()

        otp_storage.pop(email, None)  # Optional: clean up
        flash('Password reset successfully. Please log in.')
        return redirect(url_for('signin'))

    # For GET method
    email = request.args.get('email')
    return render_template('reset-password.html', email=email)



@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    data = request.get_json()
    customer_id = data.get('id')

    if not customer_id:
        return jsonify({'success': False, 'error': 'Missing ID'})

    try:
        conn = sqlite3.connect('databasewithcustomer.db')  # Change to your DB name
        c = conn.cursor()
        c.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_customer', methods=['POST'])
def save_customer():
    data = request.json
    conn = sqlite3.connect('databasewithcustomer.db')
    cursor = conn.cursor()

    if data['isEditMode']:
        # UPDATE existing customer
        cursor.execute('''
            UPDATE customers SET
                name = ?, email = ?, phone = ?, address = ?, product = ?, status = ?,
                start_date = ?, end_date = ?, warrantyYears = ?, avatar = ?
            WHERE id = ?
        ''', (
            data['name'], data['email'], data['phone'], data['address'], data['product'],
            data['status'], data['startDate'], data['endDate'],
            str(data['warrantyYears']), data['avatar'], data['id']
        ))
    else:
        # INSERT new customer
        cursor.execute('''
            INSERT INTO customers (name, email, phone, address, product, status,
                                   start_date, end_date, warrantyYears, avatar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['email'], data['phone'], data['address'], data['product'],
            data['status'], data['startDate'], data['endDate'],
            str(data['warrantyYears']), data['avatar']
        ))

    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route("/customers")
def customers():
    conn = sqlite3.connect("databasewithcustomer.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    db_rows = cursor.fetchall()
    conn.close()

    customers = []
    for row in db_rows:
        customers.append({
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            "address": row["address"],
            "product": row["product"],
            "status": row["status"].strip().lower(),
            "startDate": row["start_date"],
            "endDate": row["end_date"],
            "avatar": row["avatar"] if row["avatar"] else "https://randomuser.me/api/portraits/lego/1.jpg",
            "hasWarranty": row["warrantyYears"] != '0',
            "warrantyYears": int(row["warrantyYears"]),
            "customerId": f"CUS-{str(row['id']).zfill(3)}"
        })

    return render_template("customer2.html", customers=customers)

@app.route('/add_sample_customers')
def add_sample_customers():
    conn = sqlite3.connect('databasewithcustomer.db')
    c = conn.cursor()
     
                
    customers = [
        ('John Smith', 'john@example.com', '9876543210', '123 Main St, NY', 'CRM Software', 'Active', 'Jul 3, 2025','Jul 2, 2026', '3', 'https://randomuser.me/api/portraits/men/1.jpg'),
        ('Sarah Lee', 'sarah@example.com', '9123456789', '456 Elm St, LA', 'Analytics Tool', 'Inactive', 'June 2, 2025','June 1, 2026', '0', 'https://randomuser.me/api/portraits/women/2.jpg')
    ]
    print("inside")
    c.executemany('''
        INSERT INTO customers (name, email, phone, address, product, status, start_date, end_date, warrantyYears, avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', customers)
    print("Not executed")
    conn.commit()
    conn.close()
    return "Sample customers added!"

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("databasewithcustomer.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    conn.close()

    total_customers = len(rows)
    active_customers = 0
    inactive_customers = 0
    today = datetime.now()
    for row in rows:
        end_date = datetime.strptime(row["end_date"], "%Y-%m-%d")
        warranty_years = int(row["warrantyYears"])
        if warranty_years > 0:
            end_date += timedelta(days=warranty_years * 365)
        if today <= end_date:
            active_customers += 1
        else:
            inactive_customers += 1

    return render_template("dashboard.html",
                           total_customers=total_customers,
                           active_customers=active_customers,
                           inactive_customers=inactive_customers)

# Route for index page (admin redirect)
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/')
def home():
    return render_template('signin.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
