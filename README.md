# Todo List

A small Flask to-do list with add, edit, delete, completion toggling, status labels, and All / Active / Completed filters. Tasks are stored directly in SQLite and remain available after the app restarts.

Choose Light or Dim from the header theme menu, or select System to follow your device's color preference. Your choice is saved in this browser.

## Run locally

1. Use Python 3.9 or newer.
2. From this directory, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install Flask and start the app:

   ```powershell
   pip install -r requirements.txt
   python app.py
   ```

4. Open <http://127.0.0.1:5000>.

The database is created automatically at `instance/tasks.sqlite3`. Set the `SECRET_KEY` environment variable to a private value before deployment; the built-in development key is for local use only. Run tests with `python -m unittest discover -s tests`.
