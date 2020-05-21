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

        self.new_qst = {
            "question": {
                "question": "In which Hollywood film did Michael Jordan act?"
                , "answer": "Space Jam"
                , "category": 5
                , "difficulty": 3
                },
            "current_category": 1
        }

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
    def test_001_get_homepage(self):
        res = self.client().get('/')
        
        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            self.assertIn(b'<title>React App</title>', res.data)
            self.assertNotIn(b'Hello, World!', res.data)
    def test_002_405_post_homepage(self):
        res = self.client().post('/', json={'question': 'Is this working?'})
        
        self.assertEqual(res.status_code, 405)
        data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
        
        self.assertIsNotNone(data)
        if data:
            self.assertIn('success', data)
            self.assertIn('error_code', data)
            self.assertIn('error_name', data)
            self.assertIn('error_description', data)
        # self.assertIn(b'not allowed', res.data)

    def test_003_select_questions(self):
        stmt_sel_all_questions = text('select * from questions;')
        with self.app.app_context():           
            result = self.db.engine.execute(stmt_sel_all_questions)
        
        rows = [row for row in result]
        self.assertTrue(rows)
        if rows:
            self.assertEqual(rows[0][0], int(5))
    def test_004_column_category_name(self):
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
        
    def test_005_select_qst_with_cat(self):
        sel_stmnt = text("""
        SELECT
            q.id, q.question, q.category_id, c.id, c.type
        FROM questions as q 
            INNER JOIN categories as c on q.category_id = c.id
        ;""")

        def exec_q_or_none():
            with self.app.app_context():
                try:
                    return self.db.engine.execute(sel_stmnt)
                except DBAPIError as e:
                    print(e)
                    return None
        
        q_result = exec_q_or_none()
        self.assertIsNotNone(q_result)
        if q_result:
            rows = [row for row in q_result]
            self.assertEqual(rows[0][0], 5)
    def test_006_select_qst_where_cat_none(self):
        sel_stmnt = text("""
        SELECT q.id, q.question
        FROM questions as q
        WHERE q.category_id is null
        ;""")
        def exec_q_or_none():
            with self.app.app_context():
                try:
                    return self.db.engine.execute(sel_stmnt)
                except DBAPIError as e:
                    print(e)
                    return None
        
        q_result = exec_q_or_none()
        self.assertIsNotNone(q_result)
        if q_result:
            rows = [row for row in q_result]
            self.assertEqual(len(rows), 0)

    def test_007_get_all_questions(self):
        res = self.client().get('/api/questions')
        self.assertEqual(res.status_code, 200)

        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertEqual(data['questions'][0]['id'], 2)
    # def test_008_404_get_all_questions(self):
    #     res = self.client().get('/questions')
    #     self.assertEqual(res.status_code, 404)
    
    def test_009_pagination(self):
        res = self.client().get('/api/questions')
        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertLessEqual(len(data['questions']), QUESTIONS_PER_PAGE)
            self.assertGreaterEqual(data['total_questions'], QUESTIONS_PER_PAGE)

    def test_010_get_all_questions_of_cat_1(self):
        category_id = 1
        res = self.client().get('/api/questions/categories/' + str(category_id))
        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertEqual(len(data['questions']), 3)
            self.assertIn('questions', data)
            self.assertIn('total_questions', data)
            self.assertIn('current_category', data)
            

    def test_011_404_get_all_questions_of_cat_not_present(self):
        category_id = 100000
        res = self.client().get('/api/questions/categories/' + str(category_id))
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
        
        self.assertIsNotNone(data)
        if data:
            self.assertIn('success', data)
            self.assertIn('error_code', data)
            self.assertIn('error_name', data)
            self.assertIn('error_description', data)
        
    def test_012_get_all_categories(self):
        res = self.client().get('/api/categories')

        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertEqual(len(data['categories']), 7)
            self.assertEqual(data['categories']['1'], 'Science')

    # def test_013_404_get_category_1(self):
    #     category_id = 1
    #     res = self.client().get('/api/categories/' + str(category_id))

    #     self.assertEqual(res.status_code, 404)

    def test_014_post_question(self):
        res = self.client().post('/api/questions', json=json.dumps(self.new_qst))
        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertIn('created', data)

    def test_015_422_post_duplicate_question(self):
        res = self.client().post('/api/questions', json=json.dumps(self.new_qst))
        
        self.assertEqual(res.status_code, 422)
        data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
        
        self.assertIsNotNone(data)
        if data:
            self.assertIn('success', data)
            self.assertIn('error_code', data)
            self.assertIn('error_name', data)
            self.assertIn('error_description', data)
        
    def test_016_400_post_question_without_answer(self):
        q = {
            "question": { 
                "question": "In which Hollywood film did Michael Jordan act?"
            }
        }
        res = self.client().post(
            '/api/questions', 
            json=json.dumps(q)
            )
        self.assertEqual(res.status_code, 400)
        
        data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
        self.assertIsNotNone(data)
        if data:
            self.assertIn('success', data)
            self.assertIn('error_code', data)
            self.assertIn('error_name', data)
            self.assertIn('error_description', data)

    def test_017_delete_question(self):
        with self.app.app_context():
            search_for = '%jordan%'
            id_to_delete = self.db.session.query(Question.id).filter(Question.question.ilike(search_for)).one()._asdict()['id']
            res = self.client().delete('/api/questions/' + str(id_to_delete))
            self.assertEqual(res.status_code, 200)
            if res.status_code == 200:
                data = res.get_json()
                if isinstance(data, str):
                    data = json.loads(data)
                self.assertIn('deleted', data)

    def test_018_404_delete_non_existent_question(self):
        qst_id = 100
        res = self.client().delete('/api/questions/' + str(qst_id))
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
        self.assertIsNotNone(data)
        if data:
            self.assertIn('success', data)
            self.assertIn('error_code', data)
            self.assertIn('error_name', data)
            self.assertIn('error_description', data)
    
    def test_019_search_question_on_qst(self):
        search = json.dumps({
            "searchTerm": "a"
        })
        res = self.client().post('/api/questions/searches', json=search)

        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertEqual(data['total_questions'], 17)
    def test_020_search_question_without_result(self):
        search = json.dumps({
            "searchTerm": "afkhbfkbfkjbfiubfifbu"
            , "search_on_answer": True
        })
        res = self.client().post('/api/questions/searches', json=search)

        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertEqual(len(data['questions']), 0)

    # def test_021_search_question_on_ans(self):
    #     search = json.dumps({
    #         "searchTerm": "a"
    #         , "search_on_answer": True
    #     })
    #     res = self.client().post('/api/questions/searches', json=search)

    #     self.assertEqual(res.status_code, 200)
    #     if res.status_code == 200:
    #         data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
    #         self.assertEqual(data['total_questions'], 14)
    
    def test_022_search_category(self):
        search = json.dumps({
            "searchTerm": "a"
        })
        res = self.client().post('/api/categories/searches', json=search)

        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertEqual(data['total_categories'], 4)

    def test_023_400_search_without_term(self):
        res = self.client().post('/api/questions/searches')

        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)

        self.assertIsNotNone(data)
        if data:
            self.assertIn('success', data)
            self.assertIn('error_code', data)
            self.assertIn('error_name', data)
            self.assertIn('error_description', data)

    # def test_024_405_get_search(self):
    #     res = self.client().get('/api/questions/searches')

    #     self.assertEqual(res.status_code, 405)

    def test_025_get_random_question(self):
        play_json = json.dumps({
            'quiz_category': {'id': 0, 'type': 'all'}
            , 'previous_questions': [1, 2]
        })
        res = self.client().post('/api/questions/random', json=play_json)

        self.assertEqual(res.status_code, 200)
        if res.status_code == 200:
            data = res.get_json()
        if isinstance(data, str):
            data = json.loads(data)
            self.assertIn('question', data)
            self.assertNotEqual(2, data['question']['id'])

    # def test_026_405_post_random_question(self):
    #     res = self.client().post('/api/questions/random')

    #     self.assertEqual(res.status_code, 405)

    



    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()