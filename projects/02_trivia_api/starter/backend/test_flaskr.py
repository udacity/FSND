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
    "invalid_input": "The request could not be processed because of invalid data.",
    "bad_request": "The browser (or proxy) sent a request that this server could not understand.",
    "method_not_allowed": "The method is not allowed for the requested URL.",
    "not_found": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
    "unprocessable": "The request was well-formed but was unable to be followed due to semantic errors.",
    "internal_server_error": "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application."
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

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(
            data["message"], error_messages["method_not_allowed"])

    def test_retrieve_questions(self):
        response = self.client.get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNone(data["current_category"])
        self.assertEqual(data["total_questions"], Question.query.count())
        self.assertTrue(len(data["questions"]))

        question = data["questions"][0]
        self.assertIn("id", question)
        self.assertIn("question", question)
        self.assertIn("answer", question)
        self.assertIn("category", question)
        self.assertIn("difficulty", question)

        categories = Category.query.all()
        for category in categories:
            category_id = str(category.id)
            self.assertIn(category_id, data["categories"])
            self.assertEqual(
                data["categories"][category_id],
                category.type.lower())

    def test_retrieve_questions_when_requesting_second_page(self):
        response = self.client.get('/questions?page=2')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNone(data["current_category"])
        self.assertEqual(data["total_questions"], Question.query.count())
        self.assertTrue(len(data["questions"]))

        question = data["questions"][0]
        self.assertIn("id", question)
        self.assertIn("question", question)
        self.assertIn("answer", question)
        self.assertIn("category", question)
        self.assertIn("difficulty", question)

        categories = Category.query.all()
        for category in categories:
            category_id = str(category.id)
            self.assertIn(category_id, data["categories"])
            self.assertEqual(
                data["categories"][category_id],
                category.type.lower())

    def test_retrieve_questions_when_page_out_of_bounds(self):
        response = self.client.get('/questions?page=3')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["not_found"])

    def test_remove_question(self):
        question_id = 5
        response = self.client.delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

        question = Question.query.\
            filter(Question.id == question_id).\
            one_or_none()
        self.assertIsNone(question)

    def test_remove_question_when_question_does_not_exist(self):
        question_id = 25
        response = self.client.delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["unprocessable"])

    def test_create_question(self):
        payload = {
            "question": "What animal classification does a dog belong to?",
            "answer": "Mammal",
            "difficulty": 2,
            "category": 1
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_question_when_request_body_not_provided(self):
        response = self.client.post("/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["bad_request"])

    def test_create_question_when_requried_attribute_not_provided(self):
        payload = {
            "question": "What animal classification does a dog belong to?",
            "difficulty": 2,
            "category": 1
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["invalid_input"])

        validation_errors = data["validation_errors"]
        self.assertEqual(len(validation_errors), 1)
        self.assertEqual(validation_errors[0]["attribute"], "answer")
        self.assertEqual(validation_errors[0]["type"], "attribute_required")
        self.assertEqual(
            validation_errors[0]["message"],
            "A value is required for the attribute \"answer\".")

    def test_create_question_when_many_required_attributes_not_provided(self):
        payload = {
            "answer": "Mammal"
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["invalid_input"])

        validation_errors = data["validation_errors"]
        self.assertEqual(len(validation_errors), 3)

        errors = {
            error["attribute"]: {
                "type": error["type"],
                "message": error["message"]
            }
            for error in validation_errors
        }
        self.assertEqual(
            errors["question"]["type"],
            "attribute_required")
        self.assertEqual(
            errors["question"]["message"],
            "A value is required for the attribute \"question\".")

        self.assertEqual(
            errors["category"]["type"],
            "attribute_required")
        self.assertEqual(
            errors["category"]["message"],
            "A value is required for the attribute \"category\".")

        self.assertEqual(
            errors["difficulty"]["type"],
            "attribute_required")
        self.assertEqual(
            errors["difficulty"]["message"],
            "A value is required for the attribute \"difficulty\".")

    def test_create_question_when_category_does_not_exist(self):
        payload = {
            "question": "What animal classification does a dog belong to?",
            "answer": "Mammal",
            "difficulty": 2,
            "category": 20
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["invalid_input"])

        validation_errors = data["validation_errors"]
        self.assertEqual(len(validation_errors), 1)
        self.assertEqual(validation_errors[0]["attribute"], "category")
        self.assertEqual(validation_errors[0]["type"], "not_found")
        self.assertEqual(
            validation_errors[0]["message"],
            "A resource for the attribute \"category\" with the value \"20\" was not found.")

    def test_create_question_when_difficulty_out_of_range(self):
        payload = {
            "question": "What animal classification does a dog belong to?",
            "answer": "Mammal",
            "difficulty": 0,
            "category": 1
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["invalid_input"])

        validation_errors = data["validation_errors"]
        self.assertEqual(len(validation_errors), 1)
        self.assertEqual(validation_errors[0]["attribute"], "difficulty")
        self.assertEqual(validation_errors[0]["type"], "number_out_of_range")
        self.assertEqual(
            validation_errors[0]["message"],
            "The attribute \"difficulty\" must be an integer from 1 and 5.")

    def test_create_question_when_category_has_invalid_type(self):
        payload = {
            "question": "What animal classification does a dog belong to?",
            "answer": "Mammal",
            "difficulty": 2,
            "category": "science"
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["invalid_input"])

        validation_errors = data["validation_errors"]
        self.assertEqual(len(validation_errors), 1)
        self.assertEqual(validation_errors[0]["attribute"], "category")
        self.assertEqual(validation_errors[0]["type"], "invalid_type")
        self.assertEqual(
            validation_errors[0]["message"],
            "The attribute \"category\" must be an integer.")

    def test_create_question_when_difficulty_has_invalid_type(self):
        payload = {
            "question": "What animal classification does a dog belong to?",
            "answer": "Mammal",
            "difficulty": 'hard',
            "category": 1
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["invalid_input"])

        validation_errors = data["validation_errors"]
        self.assertEqual(len(validation_errors), 1)
        self.assertEqual(validation_errors[0]["attribute"], "difficulty")
        self.assertEqual(validation_errors[0]["type"], "invalid_type")
        self.assertEqual(
            validation_errors[0]["message"],
            "The attribute \"difficulty\" must be an integer.")

    def test_search_questions(self):
        payload = {
            "searchTerm": "egypt"
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 1)
        self.assertIsNone(data["current_category"])
        self.assertIn("questions", data)

        question = data["questions"][0]
        self.assertEqual(
            question["question"],
            "Which dung beetle was worshipped by the ancient Egyptians?")
        self.assertEqual(question["answer"], "Scarab")
        self.assertEqual(question["category"], 4)
        self.assertEqual(question["difficulty"], 4)
        self.assertEqual(question["id"], 23)

    @mock.patch("flaskr.Question")
    def test_search_questions_when_no_matching_questions(self, mock_model):
        mock_model.query.return_value.all.return_value = []
        payload = {"searchTerm": "dinosoar"}
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["questions"], [])

    def test_retreive_category_questions(self):
        category_id = 6
        response = self.client.get(f'/categories/{category_id}/questions')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["current_category"], category_id)
        self.assertEqual(data["total_questions"], 2)
        self.assertIn("questions", data)

        questions = {
            question["id"]: question
            for question in data["questions"]
        }

        self.assertIn(10, questions)
        self.assertEqual(
            questions[10]["question"],
            "Which is the only team to play in every soccer World Cup tournament?")
        self.assertEqual(questions[10]["answer"], "Brazil")
        self.assertEqual(questions[10]["category"], 6)
        self.assertEqual(questions[10]["difficulty"], 3)

        self.assertIn(11, questions)
        self.assertEqual(
            questions[11]["question"],
            "Which country won the first ever soccer World Cup in 1930?")
        self.assertEqual(questions[11]["answer"], "Uruguay")
        self.assertEqual(questions[11]["category"], 6)
        self.assertEqual(questions[11]["difficulty"], 4)

    def test_retrieve_category_questions_when_id_not_provided(self):
        response = self.client.get("/categories//questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["not_found"])

    def test_retrieve_category_questions_when_category_does_not_exist(self):
        category_id = 10
        response = self.client.get(f'/questions/{category_id}/questions')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["not_found"])

    @mock.patch("flaskr.Question")
    def test_retrieve_category_questions_when_no_category_has_not_questions(self, mock_model):
        mock_model.query.return_value.all.return_value = []
        category_id = 3
        response = self.client.get(f'/categories/{category_id}/questions')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["current_category"], category_id)
        self.assertEqual(data["total_questions"], 0)
        self.assertIn("questions", data)
        self.assertEqual(len(data["questions"]), 0)

    def test_retrieve_quiz_question_when_all_category_chosen(self):
        payload = {
            "quiz_category": {
                "id": 0
            },
            "previous_questions": []
        }
        response = self.client.post("/quizzes", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIn("question", data)

        question = data["question"]
        self.assertTrue(question["question"])
        self.assertTrue(question["answer"])
        self.assertTrue(question["category"])
        self.assertTrue(question["difficulty"])
        self.assertTrue(question["id"])

    def test_retrieve_quiz_question_when_category_chosen(self):
        payload = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        response = self.client.post("/quizzes", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIn("question", data)

        question = data["question"]
        self.assertTrue(question["question"])
        self.assertTrue(question["answer"])
        self.assertTrue(question["category"])
        self.assertTrue(question["difficulty"])
        self.assertTrue(question["id"])

    def test_retrive_quiz_question_when_category_does_not_exist(self):
        payload = {
            "quiz_category": {
                "id": 10
            },
            "previous_questions": []
        }
        response = self.client.post("/quizzes", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["type"], "invalid_request_error")
        self.assertEqual(data["message"], error_messages["invalid_input"])
        self.assertIn("validation_errors", data)

        validation_errors = data["validation_errors"]
        self.assertEqual(len(validation_errors), 1)
        self.assertEqual(validation_errors[0]["attribute"], "quiz_category.id")
        self.assertEqual(validation_errors[0]["type"], "not_found")
        self.assertEqual(
            validation_errors[0]["message"],
            "A resource for the attribute \"quiz_category.id\" with the value \"10\" was not found.")

    def test_retrieve_quiz_question_when_category_has_no_questions_remaining(self):
        payload = {
            "quiz_category": {
                "id": 6
            },
            "previous_questions": [10, 11]
        }
        response = self.client.post("/quizzes", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNone(data["question"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
