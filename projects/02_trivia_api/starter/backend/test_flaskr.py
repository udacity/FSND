import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.QUESTIONS_PER_PAGE = 10
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgres://{}/{}".format('postgres:postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question_1 = {'answer': '1', 'category': 1, 'difficulty': 1, 'question': 'new question 1'}
        self.new_question_2 = {'answer': '', 'category': '', 'difficulty': '', 'question':'' }

        self.search_term_1  = {'searchTerm': 'actor'}
        self.search_term_2  = {'searchterm': 'actor'}  # wrong requst parameter

        # when category is 'click' which menas ALL category
        self.quizzes_1 = {
            'previous_questions': [], 
            'quiz_category': {'id': 0, 'type': 'click'}
        }

        # when specify category
        self.quizzes_2 = {
            'previous_questions': [18, 19],
            'quiz_category': {'id': '1', 'type': 'Art'}
        }

        # wrong data for request as category doesn't exist
        self.quizzes_3 = {
            'previous_questions': [18, 19],
            'quiz_category': {'id': '1', 'type': 'Full Stack Web Development'}
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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test for GET '/categories'
    def test_get_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        num_of_categories = len(Category.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']),num_of_categories)

    def test_get_categories_failure(self):
        res = self.client().get('/categories/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test for GET '/categories/<int:category_id>'
    def test_get_questions_in_category_success(self):
        category_id = '1'
        res = self.client().get('/categories/'+category_id)
        data = json.loads(res.data)
        questions = Question.query.filter(Question.category==category_id).order_by(Question.id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #self.assertEqual(len(questions),data['total_questions'])
        self.assertLessEqual(data['total_questions'],self.QUESTIONS_PER_PAGE)

    def test_get_questions_in_category_failure(self):
        category_id = '0' #category doesn't exist
        res = self.client().get('/categories/'+category_id)
        data = json.loads(res.data)
        #questions = Question.query.filter(Question.category==category_id).all()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)


    # test for GET '/questions'
    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        #questions = Question.query.order_by(Question.id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)     
        self.assertLessEqual(data['total_questions'],self.QUESTIONS_PER_PAGE)

    def test_get_all_questions_failure(self):
        res = self.client().get('/questionss')
        data = json.loads(res.data)
        #questions = Question.query.order_by(Question.id).all()

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)     
        #self.assertLessEqual(data['total_questions'],self.QUESTIONS_PER_PAGE)

    # success test for DELETE '/questions/<int:question_id> '
    def test_delete_question_success(self):
        question_id = '4'
        question_pre = Question.query.filter(Question.id == question_id).one_or_none()
        res = self.client().delete('/questions/'+ question_id)
        data = json.loads(res.data)
        question_after = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)   
        self.assertIsNotNone(question_pre)      
        self.assertIsNone(question_after) 

    # failure test for DELETE '/questions/<int:question_id>
    def test_delete_question_failure(self):
        res = self.client().delete('/questions/0')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)   


    # test for POST '/questions/add'
    def test_add_question_success(self):
        same_question_pre = Question.query.with_entities(Question.id).filter(Question.question==self.new_question_1['question'],Question.answer==self.new_question_1['answer'], Question.category==self.new_question_1['category'], Question.difficulty==self.new_question_1['difficulty']).all()
        num_pre = len(same_question_pre)
        res = self.client().post('/questions/add', json=self.new_question_1)
        data = json.loads(res.data)
        same_question_now = Question.query.with_entities(Question.id).filter(Question.question==self.new_question_1['question'],Question.answer==self.new_question_1['answer'], Question.category==self.new_question_1['category'], Question.difficulty==self.new_question_1['difficulty']).all()
        num_now = len(same_question_now)
        
        self.assertEqual(num_now-num_pre,1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)

    def test_add_question_empty_value_failure(self):
        #same_question_pre = Question.query.with_entities(Question.id).filter(Question.question==self.new_question_2['question'],Question.answer==self.new_question_2['answer'], Question.category==self.new_question_2['category'], Question.difficulty==self.new_question_2['difficulty']).all()
        #num_pre = len(same_question_pre)
        res = self.client().post('/questions/add', json=self.new_question_2)
        data = json.loads(res.data)
        #same_question_now = Question.query.with_entities(Question.id).filter(Question.question==self.new_question_2['question'],Question.answer==self.new_question_2['answer'], Question.category==self.new_question_2['category'], Question.difficulty==self.new_question_2['difficulty']).all()
        #num_now = len(same_question_now)
        
        #self.assertEqual(num_now-num_pre,1)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False)


    # test for POST '/questions/search'
    def test_search_questions_success(self):
        res = self.client().post('/questions/search', json=self.search_term_1)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)

    def test_search_questions_failure(self):
        res = self.client().post('/questions/search', json=self.search_term_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'],False)

    # test for POST '/quizzes'
    def test_get_next_quizze_from_all_categories_success(self):
        res = self.client().post('/quizzes', json = self.quizzes_1)
        data= json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True) 

        id = data['question']['id']  
        self.assertNotIn(id,self.quizzes_1['previous_questions']) 


    def test_get_next_quizze_from_category_success(self):
        res = self.client().post('/quizzes', json = self.quizzes_2)
        data= json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True) 
  
        id = data['question']['id']  
        self.assertNotIn(id,self.quizzes_1['previous_questions'])

        question_category_id = data['question']['category']
        question_category_name = Category.query.with_entities(Category.type).filter(Category.id==question_category_id).one_or_none()[0]
        self.assertEqual(question_category_name, self.quizzes_2['quiz_category']['type'])

    def test_get_next_quizze_incorrect_category_failure(self):
        res = self.client().post('/quizzes', json = self.quizzes_3)
        data= json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'],False) 

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
