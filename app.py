import sqlite3
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DATABASE = "tasks.db"


# ---------- Database helpers ----------

def get_db():
    """
    Returns a database connection for the CURRENT request.
    `g` is a special Flask object that stores data only for the
    lifetime of one request, so every request gets a fresh,
    isolated connection instead of everyone sharing one.
    """
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["text"]
    return g.db


@app.teardown_appcontext
def close_db(exception):
    # Flask calls this automatically after every request finishes,
    # even if an error happened, so the connection never leaks.
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Creates the tasks table once, when the app starts, if it doesn't exist yet."""
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# ---------- Frontend route ----------

@app.route("/")
def index():
    return render_template("index.html")


# ---------- REST API routes ----------

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    db = get_db()
    rows = db.execute("SELECT id, text, done FROM tasks").fetchall()
    tasks = [dict(row) for row in rows]   # sqlite3.Row -> plain dict for jsonify
    return jsonify(tasks), 200


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Task text cannot be empty"}), 400

    db = get_db()
    cursor = db.execute("INSERT INTO tasks (text, done) VALUES (?, 0)", (text,))
    db.commit()
    new_task = {"id": cursor.lastrowid, "text": text, "done": 0}
    return jsonify(new_task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def toggle_task(task_id):
    db = get_db()
    row = db.execute("SELECT done FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        return jsonify({"error": "Task not found"}), 404

    new_status = 0 if row["done"] else 1
    db.execute("UPDATE tasks SET done = ? WHERE id = ?", (new_status, task_id))
    db.commit()
    return jsonify({"id": task_id, "done": new_status}), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    row = db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        return jsonify({"error": "Task not found"}), 404

    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return jsonify({"status": "deleted"}), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0",debug=True, port=5000)
