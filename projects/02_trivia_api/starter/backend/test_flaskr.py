import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

load_dotenv()

dbUser = os.getenv("DB_USER")
dbPwd = os.getenv("DB_PWD")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            dbUser, dbPwd,
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "What is the best football team?",
            "answer": "Fenerbahce",
            "difficulty": "5",
            "category": "6"
        }

        self.new_badQuestion = {
            "ques": "What is the best football team?",
            "ans": "Fenerbahce",
            "diff": "5",
            "cat": "6"
        }

        self.searchTerm = {
            "searchTerm": "foo"
        }

        self.badSearchTerm = {
            "searchTerm": "jkll"
        }

        self.quizRequest = {
            "previous_questions": ["17", "18"],
            "quiz_category": {
                "type": "Science",
                "id": "1"
            }
        }

        self.quizBadRequest = {
            "previous_questions": ["16", "17", "18"],
            "quiz_category": {
                "type": "Science",
                "id": "1"
            }
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

    '''
    @TODO:Write at least one test for each test
    for successful operation and for expected errors.
    '''

    '''Hello Test'''

    def test_hello(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)

    '''Get Questions Positive Test'''

    def test_getQuestions_positive(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    '''Get Questions Negative Test'''

    def test_getQuestions_negative(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    '''Delete Question Positive Test'''

    def test_deleteQuestion_positive(self):
        res = self.client().delete('/questions/40')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])

    '''Delete Question Negative Test'''

    def test_deleteQuestion_negative(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    '''Create a new question positive Test'''

    def test_createQuestion_positive(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))

    '''Search questions positive Test'''

    def test_searchQuestions_positive(self):
        res = self.client().post('/questions/search', json=self.searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))

    '''Search questions negative Test'''

    def test_searchQuestions_negative(self):
        res = self.client().post('/questions/search', json=self.badSearchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    '''Get Questions by Category Positive Test'''

    def test_getQuestionsByCategory_positive(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['currentCategory']))

    '''Get Questions by Category Negative Test'''

    def test_getQuestionsByCategory_negative(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    '''Quiz positive Test'''

    def test_quiz_positive(self):
        res = self.client().post('/quizzes', json=self.quizRequest)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    '''Quiz negative Test'''

    def test_quiz_negative(self):
        res = self.client().post('/quizzes', json=self.quizBadRequest)
        data = json.loads(res.data)

        self.assertEqual(len(data),0)
        self.assertEqual(res.status_code, 200)
       


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
