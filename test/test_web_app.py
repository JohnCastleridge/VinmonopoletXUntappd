import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import os
import sys

# Add the parent directory to the path so we can import web_app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import web_app


class TestWebApp(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        web_app.app.config["TESTING"] = True
        self.client = web_app.app.test_client()

    @patch("web_app.sqlite3.connect")
    def test_get_beers_endpoint(self, mock_connect):
        # Create a mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Configure the mock cursor to return a fake row
        fake_row = {
            "vmp_name": "Porter",
            "vmp_brewery": "Nøgne Ø",
            "unt_name": "Nøgne Ø Porter",
            "rating_score": 3.8,
        }
        mock_cursor.fetchall.return_value = [fake_row]

        # Configure the mock connection to return our mock cursor
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Test the endpoint
        response = self.client.get("/api/beers")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["vmp_name"], "Porter")
        self.assertEqual(data[0]["vmp_brewery"], "Nøgne Ø")
        self.assertEqual(data[0]["unt_name"], "Nøgne Ø Porter")
        self.assertEqual(data[0]["rating_score"], 3.8)

        # Verify that the DB was called and closed
        mock_connect.assert_called_once_with(web_app.DB_PATH)
        mock_conn.close.assert_called_once()

    def test_index_route(self):
        # We just want to check if the route exists and returns 200/404 based on static files
        # Since static/index.html might not be present in the exact CWD during tests,
        # we just ensure it doesn't 500 error.
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])


if __name__ == "__main__":
    unittest.main()
