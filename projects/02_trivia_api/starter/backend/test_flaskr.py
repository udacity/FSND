import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            "postgres", "postgres", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        self.newQuestion = {
            "question": "Who is the author of Hitchhiker's Guide to the Galaxy?",
            "answer": "Douglas Adams",
            "difficulty": "1",
            "category": "2",
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO Done
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_getCategories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_categories"])

    def test_getQuestions(self):
        res = self.client().get("/questions?page=2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))

    def test_404Error_getQuestions(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "resource not found")

    def test_createQuestion(self):
        res = self.client().post("/questions", json=self.newQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["id"])

    def test_405Error_createQuestion(self):
        res = self.client().post("/questions/24", json=self.newQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 405)
        self.assertEqual(data["message"], "method not allowed")

    def test_400Error_createQuestion(self):
        # Send wrong json
        testQuestion = {
            "wrongKey1": "Who is the author of Hitchhiker's Guide to the Galaxy?",
            "wrongKey2": "Douglas Adams",
        }
        res = self.client().post("questions", json=testQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "bad request")

    def test_deleteQuestion(self):
        res1 = self.client().post("/questions", json=self.newQuestion)
        data1 = json.loads(res1.data)
        id = data1["id"]
        res2 = self.client().delete("/questions/{}".format(id))
        data2 = json.loads(res2.data)

        self.assertEqual(res2.status_code, 200)
        self.assertEqual(data2["success"], True)
        self.assertEqual(data2["id"], id)

    def test_422Error_deleteQuestion(self):
        res1 = self.client().post("/questions", json=self.newQuestion)
        data1 = json.loads(res1.data)
        id = data1["id"]
        res2 = self.client().delete("/questions/{}".format(id + 1))
        data2 = json.loads(res2.data)

        self.assertEqual(res2.status_code, 422)
        self.assertEqual(data2["success"], False)
        self.assertEqual(data2["error"], 422)
        self.assertEqual(data2["message"], "unprocessable")

    def test_searchQuestion(self):
        res = self.client().post("/questions/search", json={"searchTerm": "movie"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_404Error_searchQuestion(self):
        res = self.client().post("/questions/search", json={"searchTerm": "blah"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "resource not found")

    def test_getQuestionsByCategory(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_404Error_getQuestionsByCategory(self):
        res = self.client().get("/categories/10/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "resource not found")

    def test_playQuiz(self):
        inputJson = {
            "previous_questions": [],
            "quiz_category": {"type": "Art", "id": 2},
        }
        res = self.client().post("/quizzes", json=inputJson)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_400Error_playQuiz(self):
        inputJson = {"previous_questions": []}
        res = self.client().post("/quizzes", json=inputJson)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], 400)
        self.assertEqual(data["message"], "bad request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()