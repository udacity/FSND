import os
import unittest
import json
# import inspect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError,DBAPIError
from flaskr import create_app, QUESTIONS_PER_PAGE
from models import setup_db, Question, Category, database_path
from psycopg2.errors import UndefinedColumn


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        self.database_path = database_path.replace('trivia', 'trivia_test')
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_homepage(self):
        res = self.client().get('/')
        
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Hello, World!', res.data)
    def test_405_post_homepage(self):
        res = self.client().post('/', json={'question': 'Is this working?'})
        
        self.assertEqual(res.status_code, 405)
        self.assertIn(b'not allowed', res.data)

    def test_select_questions(self):
        stmt_sel_all_questions = text('select * from questions;')
        with self.app.app_context():           
            result = self.db.engine.execute(stmt_sel_all_questions)
        
        rows = [row for row in result]
        self.assertTrue(rows)
        if rows:
            self.assertEqual(rows[0][0], int(5))
    def test_column_category_name(self):
        def get_category_name_or_err_code():
            stmt_sel_name_categories = text('select name from categories;')
            with self.app.app_context():
                try:
                    return self.db.engine.execute(stmt_sel_name_categories)
                except DBAPIError as e:
                    return e.orig.pgcode
        # self.assertRaises(ProgrammingError, execute_sel_category_name())
        # self.assertRaises(UndefinedColumn, execute_sel_category_name())
        # self.assertRaises(Exception("Does not work"), execute_sel_category_name())
        
        self.assertEqual('42703',get_category_name_or_err_code())
        #Error codes: https://www.psycopg.org/docs/errors.html#sqlstate-exception-classes
        
    def test_get_all_questions(self):
        res = self.client().get('/api/questions')
        self.assertEqual(res.status_code, 200)

        if res.status_code == 200:
            data = json.loads(res.data)
            self.assertEqual(data['questions'][0]['id'], 2)
    def test_404_get_all_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 404)
    
    def test_pagination(self):
        res = self.client().get('/api/questions')
        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = json.loads(res.data)
            self.assertLessEqual(len(data['questions']), QUESTIONS_PER_PAGE)
            self.assertGreaterEqual(data['total_questions'], QUESTIONS_PER_PAGE)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()