from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

BASE_DIR = Path(__file__).resolve().parent
DATABASE = str(BASE_DIR / "volunteerconnect.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-development-secret-key"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'charity'))
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL CHECK(capacity > 0),
            created_by INTEGER NOT NULL,
            FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            registered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, event_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
        );
    """)

    demo_users = [
    ("Het Soni", "het@student.example", generate_password_hash("Student123!"), "student"),
    ("Community Charity", "charity@volunteerconnect.example", generate_password_hash("Charity123!"), "charity"),
]

    for name, email, password, role in demo_users:
        conn.execute(
            "INSERT OR IGNORE INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, password, role)
        )

    count = conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"]
    if count == 0:
        charity = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("charity@volunteerconnect.example",)
        ).fetchone()
        conn.execute("""
            INSERT INTO events
            (title, description, date, time, location, capacity, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Community Food Drive",
            "Help organise and distribute food packages to local families.",
            "2026-08-15",
            "10:00",
            "Melbourne Community Centre",
            20,
            charity["id"]
        ))
        conn.execute("""
            INSERT INTO events
            (title, description, date, time, location, capacity, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Park Clean-Up",
            "Join a local clean-up activity and help improve the community environment.",
            "2026-08-20",
            "09:30",
            "Carlton Gardens",
            15,
            charity["id"]
        ))

    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, role FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    conn.close()
    return user


@app.context_processor
def inject_user():
    return {"current_user": current_user()}

@app.route("/register", methods=["POST"])
def register():
    print("REGISTER DATA:", request.form)
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        flash("Name, email and password are required.", "error")
        return render_template("login.html")

    if len(name) > 100 or len(email) > 150 or len(password) < 8:
        flash("Please provide valid details. Password must be at least 8 characters.", "error")
        return render_template("login.html")

    conn = get_db()

    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing:
        conn.close()
        flash("An account with this email already exists. Please log in.", "error")
        return render_template("login.html")

    conn.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, generate_password_hash(password), "student")
    )
    conn.commit()
    conn.close()

    flash("Account created successfully. Please log in.", "success")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        conn = get_db()
        # Parameterised query prevents SQL injection by keeping user input separate from SQL.
        user = conn.execute(
            "SELECT id, name, email, password, role FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    events = conn.execute("""
        SELECT e.*,
               u.name AS charity_name,
               (e.capacity - COUNT(r.id)) AS available_spots
        FROM events e
        JOIN users u ON u.id = e.created_by
        LEFT JOIN registrations r ON r.event_id = e.id
        GROUP BY e.id
        ORDER BY e.date ASC, e.time ASC
    """).fetchall()

    my_registrations = set()
    if current_user()["role"] == "student":
        rows = conn.execute(
            "SELECT event_id FROM registrations WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()
        my_registrations = {row["event_id"] for row in rows}

    my_events = []
    if current_user()["role"] == "charity":
        my_events = conn.execute(
            "SELECT * FROM events WHERE created_by = ? ORDER BY date ASC, time ASC",
            (session["user_id"],)
        ).fetchall()

    conn.close()
    return render_template(
        "dashboard.html",
        events=events,
        my_registrations=my_registrations,
        my_events=my_events
    )


@app.route("/event/<int:event_id>", methods=["GET", "POST"])
@login_required
def event_details(event_id):
    conn = get_db()
    event = conn.execute("""
        SELECT e.*, u.name AS charity_name,
               (e.capacity - COUNT(r.id)) AS available_spots
        FROM events e
        JOIN users u ON u.id = e.created_by
        LEFT JOIN registrations r ON r.event_id = e.id
        WHERE e.id = ?
        GROUP BY e.id
    """, (event_id,)).fetchone()

    if not event:
        conn.close()
        flash("Event not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        if current_user()["role"] != "student":
            conn.close()
            flash("Only student accounts can register for events.", "error")
            return redirect(url_for("event_details", event_id=event_id))

        if event["available_spots"] <= 0:
            conn.close()
            flash("This event is full.", "error")
            return redirect(url_for("event_details", event_id=event_id))

        try:
            conn.execute(
                "INSERT INTO registrations (user_id, event_id) VALUES (?, ?)",
                (session["user_id"], event_id)
            )
            conn.commit()
            flash("Registration successful.", "success")
        except sqlite3.IntegrityError:
            flash("You are already registered for this event.", "error")
        finally:
            conn.close()
        return redirect(url_for("event_details", event_id=event_id))

    already_registered = False
    if current_user()["role"] == "student":
        already_registered = conn.execute(
            "SELECT 1 FROM registrations WHERE user_id = ? AND event_id = ?",
            (session["user_id"], event_id)
        ).fetchone() is not None

    conn.close()
    return render_template(
        "event.html",
        event=event,
        already_registered=already_registered
    )


@app.route("/event/create", methods=["POST"])
@login_required
def create_event():
    if current_user()["role"] != "charity":
        flash("Only charity accounts can create events.", "error")
        return redirect(url_for("dashboard"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    location = request.form.get("location", "").strip()

    try:
        capacity = int(request.form.get("capacity", "0"))
    except ValueError:
        capacity = 0

    if not all([title, description, date, time, location]) or capacity <= 0:
        flash("Please provide valid information for every field.", "error")
        return redirect(url_for("dashboard"))

    if len(title) > 100 or len(location) > 150 or len(description) > 1000:
        flash("One or more fields are too long.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()
    conn.execute("""
        INSERT INTO events
        (title, description, date, time, location, capacity, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title, description, date, time, location, capacity, session["user_id"]
    ))
    conn.commit()
    conn.close()

    flash("Event created successfully.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=False)
