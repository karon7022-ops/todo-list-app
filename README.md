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

## Deploy to Azure App Service (free demo)

This app can run on **Azure App Service for Linux, F1 (Free)** for a small demo. F1 has limited shared CPU (60 CPU minutes per day), no SLA, and is intended for development and testing, not production. Availability of the free plan depends on your region and subscription.

1. In the Azure portal, create a **Web App** with **Publish: Code**, **Linux**, a supported Python runtime, and the **F1 Free** App Service plan. Connect it to the public GitHub repository `karon7022-ops/todo-list-app` for deployment, or deploy the repository contents another supported way.
2. In the Web App's **Settings → Environment variables → App settings**, add:
   - `SECRET_KEY`: a long, random secret value. For example, generate one locally with `python -c "import secrets; print(secrets.token_hex(32))"` and enter the result in Azure. Do not commit the value.
   - `DATABASE_PATH`: `/home/tasks.sqlite3`. App Service persists files under `/home`; this setting puts the SQLite database there rather than alongside deployable app files.
3. Set the **Startup Command** to `gunicorn --bind=0.0.0.0 --timeout 600 app:app`.
4. Save the settings, restart the Web App, and open its `*.azurewebsites.net` URL.

The app installs Gunicorn and Flask from the root `requirements.txt`. It refuses to start in Azure if `SECRET_KEY` is missing. The SQLite database is suitable only for this small, single-instance demo; use a managed database for a production or multi-instance app. This app has no accounts or per-user task separation, so anyone who can access the site can see and modify the same tasks. Do not use it for private or sensitive tasks.
