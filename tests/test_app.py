import os
import tempfile
import unittest

from app import create_app


class TodoListTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = os.path.join(self.temp_dir.name, "test.sqlite3")
        self.app = create_app(
            {"TESTING": True, "SECRET_KEY": "test-key", "DATABASE": self.database}
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def add_task(self, title="Write tests", status="Start"):
        return self.client.post(
            "/tasks",
            data={"title": title, "description": "A useful note", "status": status},
            follow_redirects=True,
        )

    def test_create_filter_toggle_and_persist(self):
        self.add_task()
        response = self.client.get("/?filter=active")
        self.assertIn(b"Write tests", response.data)
        self.assertIn(b"Start", response.data)

        response = self.client.post("/tasks/1/toggle", follow_redirects=True)
        self.assertIn(b"Completed", response.data)
        self.assertNotIn(b"Write tests", self.client.get("/?filter=active").data)
        self.assertIn(b"Write tests", self.client.get("/?filter=completed").data)

        self.client.post(
            "/tasks/1/edit",
            data={
                "title": "Write tests",
                "description": "A useful note",
                "status": "Completed",
            },
        )
        self.assertIn(b"Write tests", self.client.get("/?filter=completed").data)

        self.client.post("/tasks/1/toggle")
        self.assertIn(b"Write tests", self.client.get("/?filter=active").data)
        self.assertIn(b"Start", self.client.get("/?filter=active").data)

        new_app = create_app(
            {"TESTING": True, "SECRET_KEY": "test-key", "DATABASE": self.database}
        )
        persisted = new_app.test_client().get("/")
        self.assertIn(b"Write tests", persisted.data)
        self.assertIn(b"Start", persisted.data)

    def test_edit_delete_and_invalid_input(self):
        self.add_task()
        response = self.client.post(
            "/tasks/1/edit",
            data={
                "title": "Plan a project",
                "description": "Updated note",
                "status": "In progress",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Plan a project", response.data)
        self.assertIn(b"In progress", response.data)
        self.assertNotIn(b"Write tests", response.data)

        response = self.client.post(
            "/tasks", data={"title": "   ", "status": "Start"}, follow_redirects=True
        )
        self.assertIn(b"A task title is required.", response.data)
        self.assertEqual(self.client.get("/").data.count(b"task-card"), 1)

        response = self.client.post("/tasks/1/delete", follow_redirects=True)
        self.assertIn(b"A fresh start", response.data)

    def test_rejects_unknown_filter(self):
        self.assertEqual(self.client.get("/?filter=archived").status_code, 400)

    def test_theme_menu_and_theme_script_are_available(self):
        response = self.client.get("/")
        self.assertIn(b'id="theme-select"', response.data)
        self.assertIn(b'value="system"', response.data)
        self.assertIn(b'value="light"', response.data)
        self.assertIn(b'value="dim"', response.data)

        script = self.client.get("/static/theme.js")
        self.assertEqual(script.status_code, 200)
        self.assertIn(b"prefers-color-scheme: dark", script.data)
        script.close()


if __name__ == "__main__":
    unittest.main()
