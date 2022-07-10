import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Actor, Movie

class CATestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        DB_URL = "postgresql://postgres:gravity@localhost:5432/postgres"        
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app, self.DB_PATH)

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

    def test_get_actors(self):
        ASSISTANT_JWT = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRmdjZaUTNwZEpvLXNlRUJ0RERiRiJ9.eyJpc3MiOiJodHRwczovL2Rldi1nYXJ2aXRhLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MjdjMDIxNmRmMWNiZDAwNmY0ZTkxZmIiLCJhdWQiOiJjYXN0aW5nX2FnZW5jeSIsImlhdCI6MTY1NzQ4NDY4NiwiZXhwIjoxNjU3NDkxODg2LCJhenAiOiJocDBYVTh5Y3U1QkcwNDhTQTJkOUxkT0haRUNqdlJIZyIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.u2z_6yvCZ_SF68ok3YsG7jP4QDc1HctL5fzNyqQRPpK7SlN4wbiKB9yTs4BTtxIojYZ6MDCiM6x4zlkmZk1ynWpwD9MwGW0PkYcKPUz_HdsAbp10J1Mjf0fNtSgHeH1IWrXgci3e-oxA9v0v6OQmpPkuSgOKsiRZx62ELK4J5rlW-4ArFuk3qZNUKWMnUj0MAzSxnxvz4nobCRMvxiOwtrd8B76brwXviEYPT_Fp1HZbcpw6MOPsLacaWIshuKlx2e4NFj5o-TnD0UAZ2zs37h_I0BoFuCGZRYro7tNPnlPx_B7-1G56fYf6AB9t3iSyoPvKgSOxP1jRz6ilpOVuZQ'
        res = self.client().get('/actors?page=1', headers = {'Authorization': 'Bearer ' + ASSISTANT_JWT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_actors(self):
        DIRECTOR_JWT = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRmdjZaUTNwZEpvLXNlRUJ0RERiRiJ9.eyJpc3MiOiJodHRwczovL2Rldi1nYXJ2aXRhLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwODY4MDQzNzczMDI2NzcwMTg4MiIsImF1ZCI6ImNhc3RpbmdfYWdlbmN5IiwiaWF0IjoxNjU3NDM3NzQ1LCJleHAiOjE2NTc0NDQ5NDUsImF6cCI6ImhwMFhVOHljdTVCRzA0OFNBMmQ5TGRPSFpFQ2p2UkhnIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3IiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9yIiwicG9zdDphY3RvcnMiXX0.i5zdiABCfUcd-4XPrgvq3lbgrvuWF5ZbcwsmFC3tKGqrPZjPsQPqZRKf5VAr1Z8U8ftK9HbWXKuV26Wont34r8ui_VPwboZXYJMi8n61giEup2vAlcXdUPVY8Ylz_wq_-FwkaRFAICSijhTbyGFUyezO9WI-KmcXCl6-yVzXyESPo5c9trGrdFTkyp8dIdmQvzasjKbJwvIVpEBoF8s16ce2nnj4bGZyZxGalvchwGJAKStnNfzCo9pm0jamD6ji84mjkMvk_zT9faeKVrGTVEFvOLD0hvvAUt5g0n7HgvnxAXC5ycLjC9jAiH6BFa8_B8sySiH3O1khWXJV77HgHw'
        res = self.client().get('/actors?page=1', headers = {'Authorization': 'Bearer ' + DIRECTOR_JWT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_add_actor(self):
        test_actor = {'name': '', 'age': '', 'gender': ''}
        res = self.client().post('/actors', json = test_actor)
        data = json.loads(res.data)
        if data['error'] == 404:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)
        else:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)

    def test_404_add_actor(self):
        test_actor = {}
        res = self.client().post('/actors', json = test_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_actor(self):
        res = self.client().delete('/actor/1')
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == 14).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(actor, None)

    def test_404_delete_actor(self):
        res = self.client().delete('/actor/99')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()