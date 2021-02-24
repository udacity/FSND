
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from app import create_app
from models import setup_db, Movie, Actor
from config import Authtoken


"""This class represents the trivia test case"""
class CapstoneTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        # self.app.config.from_object('config')
        self.client = self.app.test_client
        # self.database_name = 'capstone.db'
        # project_dir = os.path.dirname(os.path.abspath(__file__))
        # self.database_path = "sqlite:///{}".format(os.path.join(project_dir, self.database_name))
        self.database_path = 'postgresql://postgres:postgres@localhost:5432/Capstone'

        setup_db(self.app, self.database_path)

        self.new_actor_1 = {'name': 'lili', 'age': '30', 'gender': 'F'}
        self.new_actor_2 = {}

        self.new_movie_1 = {'title': 'Lion King', 'release_date': '5/30/2022'}
        self.new_movie_2 = {}

        self.jwt_Assistant = {
            # 'Content-Type': 'application/json',
            'Authorization': Authtoken['casting_assistant']
        }

        self.jwt_Director = {
            'Content-Type': 'application/json',
            'Authorization': Authtoken['casting_director']
        }

        self.jwt_Producer = {
            'Content-Type': 'application/json',
            'Authorization': Authtoken['executive_producer']
        }
        

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        pass


    # test for GET '/actors'
    def test_get_actors_success(self):
        res = self.client().get('/actors', headers = self.jwt_Assistant)
        data = json.loads(res.data)
        num_of_actors = len(Actor.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['actors']),num_of_actors)


    def test_get_actors_failure(self):
        res = self.client().get('/actorss', headers = self.jwt_Assistant)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test for GET '/movies'
    def test_get_movies_success(self):
        res = self.client().get('/movies', headers = self.jwt_Assistant)
        data = json.loads(res.data)
        num_of_movies = len(Movie.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['movies']),num_of_movies)


    def test_get_movies_failure(self):
        res = self.client().get('/movies/', headers = self.jwt_Assistant)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test for DELETE '/actors/<int:actor_id>'
    def test_delete_actor_success(self):
        actor_id = '1'
        actor_pre = Actor.query.filter(Actor.id == actor_id).one_or_none()
        res = self.client().delete('/actors/'+ actor_id, headers = self.jwt_Producer)
        data = json.loads(res.data)
        actor_after = Actor.query.filter(Actor.id == actor_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)   
        self.assertIsNotNone(actor_pre)      
        self.assertIsNone(actor_after) 

    def test_delete_actor_failure(self):
        res = self.client().delete('/actors/0', headers = self.jwt_Producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)   


    # test for DELETE '/movies/<int:movie_id>'
    def test_delete_Movie_success(self):
        movie_id = '1'
        movie_pre = Movie.query.filter(Movie.id == movie_id).one_or_none()
        res = self.client().delete('/movies/'+ movie_id, headers = self.jwt_Producer)
        data = json.loads(res.data)
        movie_after = Movie.query.filter(Movie.id == movie_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)   
        self.assertIsNotNone(movie_pre)      
        self.assertIsNone(movie_after) 

    def test_delete_Movie_failure(self):
        res = self.client().delete('/actors/0', headers = self.jwt_Producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False) 


    # test for POST '/actors/add'
    def test_add_actor_success(self):
        same_actor_pre = Actor.query.with_entities(Actor.id)    \
            .filter(Actor.name==self.new_actor_1['name'], Actor.age==self.new_actor_1['age'], Actor.gender==self.new_actor_1['gender'])  \
            .all()
        num_pre = len(same_actor_pre)
        res = self.client().post('/actors/add', headers = self.jwt_Producer, json=self.new_actor_1)
        data = json.loads(res.data)
        same_actor_now = Actor.query.with_entities(Actor.id)    \
            .filter(Actor.name==self.new_actor_1['name'], Actor.age==self.new_actor_1['age'], Actor.gender==self.new_actor_1['gender'])  \
            .all()
        num_now = len(same_actor_now)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(num_now-num_pre,1)


    def test_add_actor_failure(self):

        res = self.client().post('/actors/add', headers = self.jwt_Producer, json=self.new_actor_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)


    # test for POST '/movies/add'
    def test_add_movie_success(self):
        same_movie_pre = Movie.query.with_entities(Movie.id)    \
            .filter(Movie.title==self.new_movie_1['title'], Movie.release_date==self.new_movie_1['release_date'])  \
            .all()
        num_pre = len(same_movie_pre)
        res = self.client().post('/movies/add', headers = self.jwt_Producer, json=self.new_movie_1)
        data = json.loads(res.data)
        same_movie_now = Movie.query.with_entities(Movie.id)    \
            .filter(Movie.title==self.new_movie_1['title'], Movie.release_date==self.new_movie_1['release_date'])  \
            .all()
        num_now = len(same_movie_now)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(num_now-num_pre,1)


    def test_add_movie_failure(self):

        res = self.client().post('/movies/add', headers = self.jwt_Producer, json=self.new_movie_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)



    # test for PATCH '/actors/<int:actor_id>'
    def test_update_actor_success(self):
        res = self.client().patch('actors/15', headers = self.jwt_Director, json=self.new_actor_1)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)


    def test_update_actor_failure(self):

        res = self.client().patch('/actors/2', headers = self.jwt_Director, json=self.new_actor_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)



    # test for PATCH '/movies/<int:movie_id>'
    def test_update_movie_success(self):
        res = self.client().patch('/movies/3', headers = self.jwt_Producer, json=self.new_movie_1)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)

    def test_add_movie_failure(self):

        res = self.client().patch('/movies/1', headers = self.jwt_Producer, json=self.new_movie_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'],False)


    def test_create_new_actor_casting_assistant(self):
        res = self.client().post('/actors/add', headers=self.jwt_Assistant, json=self.new_actor_1)
        data =  json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)


    def test_get_actors_casting_assistant(self):
        res  = self.client().get('/actors', headers = self.jwt_Assistant)
        data =  json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_add_movie_casting_director(self):
        res = self.client().post('/movies/add', headers = self.jwt_Director, json=self.new_movie_1)
        data =  json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_add_movie_casting_director(self):
        res = self.client().post('/actors/add', headers = self.jwt_Producer, json=self.new_actor_1)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()