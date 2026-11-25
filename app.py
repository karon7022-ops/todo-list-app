import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, current_app, flash, g, redirect, render_template, request, url_for


TASK_STATUSES = ("Start", "In progress")
FILTERS = ("all", "active", "completed")


def create_app(test_config=None):
    app = Flask(__name__)
    configured_secret = os.environ.get("SECRET_KEY")
    if (
        not configured_secret
        and os.environ.get("WEBSITE_SITE_NAME")
        and not (test_config and test_config.get("SECRET_KEY"))
    ):
        raise RuntimeError("Set the SECRET_KEY app setting before starting in Azure.")

    app.config.from_mapping(
        SECRET_KEY=configured_secret or "change-this-secret-key",
        DATABASE=os.environ.get(
            "DATABASE_PATH", str(Path(app.instance_path) / "tasks.sqlite3")
        ),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    initialize_database(app)

    @app.teardown_appcontext
    def close_database(_error=None):
        database = g.pop("database", None)
        if database is not None:
            database.close()

    @app.get("/")
    def index():
        selected_filter = request.args.get("filter", "all")
        if selected_filter not in FILTERS:
            abort(400, description="Filter must be all, active, or completed.")

        database = get_database()
        if selected_filter == "active":
            tasks = database.execute(
                "SELECT * FROM tasks WHERE status != 'Completed' ORDER BY id DESC"
            ).fetchall()
        elif selected_filter == "completed":
            tasks = database.execute(
                "SELECT * FROM tasks WHERE status = 'Completed' ORDER BY id DESC"
            ).fetchall()
        else:
            tasks = database.execute(
                "SELECT * FROM tasks ORDER BY id DESC"
            ).fetchall()

        counts = database.execute(
            """SELECT COUNT(*) AS total,
                      SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed
               FROM tasks"""
        ).fetchone()
        return render_template(
            "index.html",
            tasks=tasks,
            selected_filter=selected_filter,
            total_count=counts["total"],
            completed_count=counts["completed"] or 0,
            task_statuses=TASK_STATUSES,
        )

    @app.post("/tasks")
    def add_task():
        title, description, status = read_task_form()
        error = validate_task(title, description, status)
        if error:
            flash(error, "error")
            return redirect(url_for("index"))

        database = get_database()
        database.execute(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
            (title, description, status),
        )
        database.commit()
        flash("Task added.", "success")
        return redirect(url_for("index"))

    @app.route("/tasks/<int:task_id>/edit", methods=("GET", "POST"))
    def edit_task(task_id):
        task = get_task(task_id)
        if request.method == "POST":
            title, description, status = read_task_form()
            error = validate_task(title, description, status, allow_completed=True)
            if error:
                flash(error, "error")
                return redirect(url_for("edit_task", task_id=task_id))

            get_database().execute(
                "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?",
                (title, description, status, task_id),
            )
            get_database().commit()
            flash("Task updated.", "success")
            return redirect(url_for("index"))

        return render_template("edit.html", task=task, task_statuses=TASK_STATUSES)

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        task = get_task(task_id)
        new_status = "Start" if task["status"] == "Completed" else "Completed"
        database = get_database()
        database.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id)
        )
        database.commit()
        flash("Task marked as " + new_status.lower() + ".", "success")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        get_task(task_id)
        database = get_database()
        database.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        database.commit()
        flash("Task deleted.", "success")
        return redirect(url_for("index"))

    return app


def get_database():
    if "database" not in g:
        g.database = sqlite3.connect(current_app.config["DATABASE"])
        g.database.row_factory = sqlite3.Row
    return g.database


def initialize_database(app):
    database = sqlite3.connect(app.config["DATABASE"])
    try:
        database.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   description TEXT NOT NULL DEFAULT '',
                   status TEXT NOT NULL CHECK (status IN ('Start', 'In progress', 'Completed')),
                   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
               )"""
        )
        database.commit()
    finally:
        database.close()


def get_task(task_id):
    task = get_database().execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if task is None:
        abort(404)
    return task


def read_task_form():
    return (
        request.form.get("title", "").strip(),
        request.form.get("description", "").strip(),
        request.form.get("status", "Start").strip(),
    )


def validate_task(title, description, status, allow_completed=False):
    if not title:
        return "A task title is required."
    if len(title) > 120:
        return "Task titles must be 120 characters or fewer."
    if len(description) > 500:
        return "Descriptions must be 500 characters or fewer."
    valid_statuses = TASK_STATUSES + (("Completed",) if allow_completed else ())
    if status not in valid_statuses:
        return "Choose a valid task status."
    return None


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
