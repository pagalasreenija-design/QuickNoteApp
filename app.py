from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mysecretkey123"

# Create database
conn = sqlite3.connect("notes.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    note TEXT,
    created_at TEXT,
    pinned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()
conn.close()

@app.route("/")
def home():

  if "user_id" not in session:
      return redirect("/login")
  conn = sqlite3.connect("notes.db")
  cursor = conn.cursor()

  cursor.execute(
    "SELECT id, note, created_at, pinned FROM notes WHERE user_id=? ORDER BY pinned DESC, id DESC",
    (session["user_id"],)
)        
  notes = cursor.fetchall()

  conn.close()

  return render_template("index.html", notes=notes or[])

@app.route("/save", methods=["POST"])
def save_note():
    data = request.json
    note = data["note"]

    from datetime import datetime
    current_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO notes(user_id, note, created_at) VALUES(?, ?, ?)",
    (session["user_id"], note, current_time)
)

    conn.commit()
    conn.close()

    return jsonify({"message": "Note saved successfully"})
@app.route("/notes")
def get_notes():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
    "SELECT id, note, created_at, pinned FROM notes WHERE user_id=? ORDER BY pinned DESC, id DESC",
    (session["user_id"],)
)
    notes = cursor.fetchall()

    conn.close()

    return jsonify(notes)
@app.route("/delete/<int:id>", methods=["POST"])
def delete_note(id):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Note deleted successfully"})
@app.route("/edit/<int:id>", methods=["POST"])
def edit_note(id):
    data = request.json
    new_note = data["note"]

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE notes SET note=? WHERE id=?",
        (new_note, id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Note updated successfully"})
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("notes.db", timeout=10)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users(username, email, password) VALUES(?, ?, ?)",
                (username, email, hashed_password)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            return "Username or Email already exists"

        finally:
            conn.close()

        return redirect("/login")

    return render_template("signup.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()

        cursor.execute(
    "SELECT * FROM users WHERE email=?",
    (email,)
)

        user = cursor.fetchone()
        conn.close()
        

        if user and check_password_hash(user[3], password):
          session["user_id"] = user[0]
          session["username"] = user[1]
          return redirect("/")
        else:
          return "Invalid Email or Password"

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)