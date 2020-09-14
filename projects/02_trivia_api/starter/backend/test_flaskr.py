import os
import unittest
import json
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app, QUESTIONS_PER_PAGE
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        # create app and client
        self.app = create_app()

        # create test client
        self.client = self.app.test_client()

        self.database_name = "trivia_test"
        self.database_user = "trivia_test_user"
        self.database_path = "postgres://{}@{}/{}".format(
            f"{self.database_user}", "localhost:5432", self.database_name
        )

        # need to bind app to current context
        self.context = self.app.app_context()

        # push current context with requests
        self.context.push()

        # this is redundant?
        setup_db(self.app, self.database_path)

        # create sqlalchemy object
        self.db = SQLAlchemy()

        # init app
        self.db.init_app(self.app)

        # create all tables
        self.db.create_all()

        # test vars
        self.new_question = {
            "question": "What is my favorite color?",
            "answer": "Blue",
            "category": 3,
            "difficulty": 2,
        }

        self.search_term = "color"
        self.search_json_data = jsonify({"searchTerm": "color"})

        self.game = {"quiz_category": None, "previous_questions": []}

    def tearDown(self):
        """Executed after each test"""
        # clean up db
        self.db.session.remove()
        self.db.drop_all()
        self.context.pop()
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_can_get_all_categories(self):
        """ test that API can get all categories"""
        count_categories = Category.query.count()

        response = self.client.get("/api/categories")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get("categories")), count_categories)

    def test_get_questions(self):
        """
        test that API can get questions
        """
        category_count = Category.query.count()
        first_category = Category.query.order_by(Category.type.asc()).first()
        questions = Question.query.all()

        response = self.client.get("/api/questions")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["questions"]), len(questions[0:QUESTIONS_PER_PAGE]))
        self.assertEqual(data["total_questions"], len(questions))
        self.assertEqual(data["current_category"], first_category.id)
        self.assertEqual(len(data["categories"]), category_count)

    def test_404_when_get_questions(self):
        """
        test for 404 response when unreachable page is requested
        """
        response = self.client.get("/api/questions?page=1990")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_get_questions_by_category(self):
        """
        test api can get questions by category id
        """
        category_count = Category.query.count()
        questions = Question.query.filter_by(category="1").all()

        response = self.client.get("/api/categories/1/questions")
        data = json.loads(response.data)
        self.assertEqual(len(data["questions"]), len(questions[0:QUESTIONS_PER_PAGE]))
        self.assertEqual(data["total_questions"], len(questions))
        self.assertEqual(data["current_category"], 1)
        self.assertEqual(len(data["categories"]), category_count)

    def test_404_when_get_questions_by_category(self):
        """
        test api returns 404 when requesting q's for bad category
        """
        response = self.client.get("/api/categories/666/questions")
        self.assertEqual(response.status_code, 404)

    def test_delete_question(self):
        """
        test api can delete question
        """
        question = Question.query.order_by(Question.id.asc()).first()
        question_id = question.id

        response = self.client.delete(f"/api/questions/{question_id}")
        self.assertEqual(response.status_code, 204)

        deleted = Question.query.get(question_id)
        self.assertIsNone(deleted)

    def test_404_when_delete_question(self):
        """
        test api returns 404 when deleting non existent question
        """
        response = self.client.delete(f"/api/questions/990923")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_create_question(self):
        """
        test api can create question
        """
        response = self.client.post("/api/questions/create", json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone([data["id"]])
        self.assertEqual(data["question"], self.new_question["question"])
        self.assertEqual(data["answer"], self.new_question["answer"])
        self.assertEqual(data["category"], self.new_question["category"])
        self.assertEqual(data["difficulty"], self.new_question["difficulty"])

        created = Question.query.filter_by(id=data["id"]).first()
        self.assertIsNotNone(created)
        self.assertEqual(data["question"], created.question)
        self.assertEqual(data["answer"], created.answer)
        self.assertEqual(data["category"], created.category)
        self.assertEqual(data["difficulty"], created.difficulty)

    def test_search_question(self):
        """
        test api can search questions by query term
        """
        questions = Question.query.filter(
            Question.question.ilike(f"%{self.search_term}%")
        ).all()
        results = [q.format() for q in questions]

        response = self.client.post(
            "http://localhost:5000/api/questions",
            json=({"searchTerm": self.search_term}),
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["questions"]), len(results))

        for q in data["questions"]:
            self.assertIn(self.search_term.lower(), q["question"].lower())

    def test_play_game_with_all_categories(self):
        """
        Test API can play the quiz with any category
        """
        response = self.client.post("/api/quizzes", json=self.game)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["question"])
        self.assertTrue(data["quiz_category"])

    def test_play_game_with_specific_category(self):
        """
        Test API can play the quiz with a specific category
        of questions
        """
        category = 1
        self.game["quiz_category"] = {"id": category}
        response = self.client.post("/api/quizzes", json=self.game)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], category)
        self.assertTrue(data["question"])
        self.assertEqual(data["quiz_category"]["id"], category)

        self.game["quiz_category"]["id"] = category = 3
        response = self.client.post("/api/quizzes", json=self.game)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], category)
        self.assertTrue(data["question"])
        self.assertEqual(data["quiz_category"]["id"], category)

    def test_play_game_with_previous_questions(self):
        """
        Test API can play the quiz after the last question
        being answered
        """
        category = 4
        self.game["quiz_category"] = {"id": category}

        for _ in range(5):
            response = self.client.post("/api/quizzes", json=self.game)
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data["question"])
            self.assertTrue(data["question"]["id"])
            self.assertTrue(data["quiz_category"])
            self.assertTrue(data["quiz_category"]["id"])
            self.assertEqual(data["quiz_category"]["id"], category)

            if len(self.game["previous_questions"]):
                self.assertNotIn(
                    data["question"]["id"], self.game["previous_questions"]
                )

            self.game["previous_questions"].append(data["question"]["id"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

