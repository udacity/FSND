import os
import subprocess
import unittest
import json
from subprocess import DEVNULL
from unittest import mock
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

load_dotenv()
database_password = os.getenv('DB_PASSWORD', '')
error_messages = {
    "method_not_allowed": "The method is not allowed for the requested URL."
}


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    @classmethod
    def setUpClass(cls):
        subprocess.run(
            ["dropdb", "trivia_test", "--if-exists"],
            stdout=DEVNULL)
        subprocess.run(
            ["createdb", "trivia_test"],
            stdout=DEVNULL)
        subprocess.run(
            ["psql", "-f", "trivia.psql", "trivia_test"],
            stdout=DEVNULL)

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'trivia_app', database_password,
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_retrieve_categories(self):
        response = self.client.get("/categories")
        data = json.loads(response.data)
        categories = Category.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIn("categories", data)

        for category in categories:
            category_id = str(category.id)
            self.assertIn(category_id, data["categories"])
            self.assertEqual(data["categories"][category_id], category.type)

    @mock.patch("flaskr.Category")
    def test_retrieve_categories_when_returning_no_categories(self, mock_model):
        mock_model.query.return_value.all.return_value = []
        response = self.client.get("/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIn("categories", data)
        self.assertEqual(data["categories"], {})

    def test_retrieve_categories_when_incorrect_method_used(self):
        response = self.client.post("categories")
        data = json.loads(response.data)

        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(
            data["message"], error_messages['method_not_allowed'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
