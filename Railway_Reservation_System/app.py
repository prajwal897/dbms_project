from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "railwaysecret"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="railway_db"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except mysql.connector.errors.IntegrityError:
            flash("Email already exists!", "error")
        finally:
            c.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = c.fetchone()
        c.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "error")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trains")
    trains = c.fetchall()
    c.close()
    conn.close()

    return render_template('dashboard.html', trains=trains)

# ===== Add Train Route =====
@app.route('/add_train', methods=['GET', 'POST'])
def add_train():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        train_name = request.form['train_name']
        source = request.form['source']
        destination = request.form['destination']
        seats = int(request.form['seats'])

        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO trains (train_name, source, destination, seats) VALUES (%s, %s, %s, %s)",
            (train_name, source, destination, seats)
        )
        conn.commit()
        c.close()
        conn.close()
        flash("Train added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_train.html')
# ========================

@app.route('/book/<int:train_id>', methods=['GET', 'POST'])
def book(train_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trains WHERE id=%s", (train_id,))
    train = c.fetchone()

    if request.method == 'POST':
        seats = int(request.form['seats'])
        if seats <= 0 or seats > train[4]:
            flash("Invalid number of seats!", "error")
        else:
            new_seats = train[4] - seats
            c.execute("UPDATE trains SET seats=%s WHERE id=%s", (new_seats, train_id))
            c.execute("INSERT INTO bookings (user_id, train_id, seats) VALUES (%s, %s, %s)",
                      (session['user_id'], train_id, seats))
            conn.commit()
            flash("Booking successful!", "success")
            c.close()
            conn.close()
            return redirect(url_for('view_bookings'))

    c.close()
    conn.close()
    return render_template('booking.html', train=train)

@app.route('/view')
def view_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT b.id, t.train_name, b.seats 
        FROM bookings b 
        JOIN trains t ON b.train_id = t.id
        WHERE b.user_id=%s
    """, (session['user_id'],))
    data = c.fetchall()
    c.close()
    conn.close()

    return render_template('view_booking.html', data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)