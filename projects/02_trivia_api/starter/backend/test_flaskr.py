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
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path='postgresql://postgres:12345@localhost:5432/trivia_test'
        setup_db(self.app, self.database_path)

        self.new_question = Question(
            question = 'What is the fifth day of the week?',
            answer = 'the fifth',
            category ='1',
            difficulty = 0
        )


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    # ---------------------- test GET categories ------------------------------
    
    def test_get_categories(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])

    # ---------------------- test GET questions ------------------------------

    def test_get_questions(self):
        res=self.client().get('/questions',json={'page':2})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']),10)
        self.assertEqual(len(data['categories']),6)
        self.assertEqual(data['current_category'], None)
    
    # ---------------------- test POST serarchTerm ------------------------------

    def test_questions_through_search(self):
        res=self.client().post('/questions',json={'searchTerm':'taj'})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']),1)

    # ---------------------- test POST new question ------------------------------
    
    def test_adding_new_question(self):
        res = self.client().post('/questions/new', json=self.new_question.format())
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)

    # ---------------------- test DELETE a question ------------------------------
    
    # Success
    def test_deleting_question(self):
        new_question = self.new_question
        new_question.insert()
        res = self.client().delete('/questions/{}'.format(new_question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # Error
    def test_404_error_deleting_question(self):
        new_question = self.new_question
        new_question.insert()
        res = self.client().delete('/questions/8000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # ---------------------- test GET questions by categories ------------------------------
    
    def test_getting_questions_by_categories(self):
        res=self.client().get('/categories/5/questions')
        data=json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'],'5')

    # ---------------------- test getting quiz questions ------------------------------

    def test_getting_quiz_questions(self):
        res=self.client().post('/quizzes',json={'quiz_category':{'id': '1'},'previous_questions':[]})
        data=json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()