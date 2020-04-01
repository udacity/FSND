import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_question_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['categories'], ['Science',
                                              'Art',
                                              'Geography',
                                              'History',
                                              'Entertainment',
                                              'Sports'])
        self.assertEqual(data['total_categories'], 6)

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], [
            "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
            "What boxer's original name is Cassius Clay?",
            "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
            "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?",
            "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?",
            "Which is the only team to play in every soccer World Cup tournament?",
            "Which country won the first ever soccer World Cup in 1930?",
            "Who invented Peanut Butter?",
            "What is the largest lake in Africa?",
            "In which royal palace would you find the Hall of Mirrors?"
        ])
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(data['current_category'], ['Science',
                                                    'Art',
                                                    'Geography',
                                                    'History',
                                                    'Entertainment',
                                                    'Sports'])
        self.assertEqual(data['categories'], ['Science',
                                              'Art',
                                              'Geography',
                                              'History',
                                              'Entertainment',
                                              'Sports'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()