
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie

class MovieAgencyTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        # binds the app to the current context
        self.database_name = "capstonedb"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'adil1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        EXECUTIVE_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IndaUHJBLTNkemg4M05EU19ndjdyNiJ9.eyJpc3MiOiJodHRwczovL2Rldi1tZC04Z2U5Zi51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwMjE2NGRhMWY2MDMwMDE5YjA3YTJmIiwiYXVkIjoibW92aWVfcHJvZHVjZXIiLCJpYXQiOjE1OTQ0MDQwNzksImV4cCI6MTU5NDQ5MDQ3OSwiYXpwIjoiRnhCR2hrc3hseTMyamd6MFY3QTdLZGlhek1TY09wU2siLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvcnMiLCJkZWxldGU6bW92aWVzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6bW92aWVzIl19.RQs5jWa7yvFEy1q58B-gy76Vtw48T16OHMHXqOcDeVufs_hJ0h-iy3J8dXKne9Cz7TRMiobvvHkrSBqGF1XOT3X4SYyAOgXdu45YgUdVZigpgnH-4SHSCeP6SEK0UZaNvncXioznfvUIXFrQQHW3sZXBtQaSUFFEEYhD50Gy3gdm6dd9Jq2fBtkXW6cHkEtqoVqYdPkiFhtMLCD8KNbk0t3vA6PiXOgFV6S5Rtlq2s08nh3jYz98ZwSLlg96wtQSdKLc6jXU6snWOGrRecWosozD_6mt5knmUPc4CmwUUOY0Xg0Io3sw1PM38SfQRL3DbvMbYaZPTChxnYSe_oN71g'
        CASTING_DIRECTOR = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IndaUHJBLTNkemg4M05EU19ndjdyNiJ9.eyJpc3MiOiJodHRwczovL2Rldi1tZC04Z2U5Zi51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwNzdjMGZmZDMwZTIwMDEzNjY1MDA1IiwiYXVkIjoibW92aWVfcHJvZHVjZXIiLCJpYXQiOjE1OTQ0MDU3NzgsImV4cCI6MTU5NDQ5MjE3OCwiYXpwIjoiRnhCR2hrc3hseTMyamd6MFY3QTdLZGlhek1TY09wU2siLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvcnMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBvc3Q6YWN0b3JzIl19.pi_5whggjUTeazg80Jd66x0Et7fgn6DC828M2vKaVT0Fy5A2GpjPe6WQtHKLHF8Sf0_r-SUGpNTjakp44xBEZxEeTMft3qS6beHTfhU2Y1Op3K1bD2ExNBS5dEZYCBCFNzs3WBHXGgKQaACww82BnSE4kK0lYsZKMLl4k1jMKtxi_ZsS_RuS-MTMrMHiKClIPzssTuh3Bb7fWBpb1fPAPYCN3c6vWonBAJqeKKI4Q2PInYw1jlS68OKJFOWSkNUNzvJKwVJWhrqzk-IvPvbdjuhz24on5_BoB3PmOjTk7xr_KAT9WH5gXuhaFPc5zIT1_3pSWmwPy4ensHAWvRCRHw'
        ASSISTANT_DIRECTOR = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IndaUHJBLTNkemg4M05EU19ndjdyNiJ9.eyJpc3MiOiJodHRwczovL2Rldi1tZC04Z2U5Zi51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwOGIzNGVhMTViN2IwMDEzNjIwOWJhIiwiYXVkIjoibW92aWVfcHJvZHVjZXIiLCJpYXQiOjE1OTQ0MDU5NjUsImV4cCI6MTU5NDQ5MjM2NSwiYXpwIjoiRnhCR2hrc3hseTMyamd6MFY3QTdLZGlhek1TY09wU2siLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIl19.mS-xrmUbuFuQ5b7iV_mZlaoZ2wBRFbq5tpDS2z5VfGDE-yeILHxoGvqgClqX7G2P1HVrHjnwKI5oTtIskmZp_u5zvucbPYaYDn2iOVOw7exJFDeAOKKMo6zs3kGyDD2XdrWIqCA6CxoJQ5_GkMItkorhy-1GEQgb5FdARrbinUZ_fDB0u8LZiR1jpu7DvuPgD8e6XWdTij6SDhkfXmzvZHRkpi-TOT96OdhYj2cR5wFCKjj82CPllCWkDnw8ebGqsvRXluXUKzwXbIVqL8sjSvgtVqzs7qok-CO_bkp3YZuf0_RWRD7FVX1oRaBmp0InD2dmWzTn8PKcPirZXlWufg'


        CA_TOKEN = os.getenv("ASSISTANT_DIRECTOR")
        # Casting Director (CA role + can add, delete, patch actors and movies)
        CD_TOKEN = os.getenv("CASTING_DIRECTOR")

        ED_TOKEN = os.getenv("EXECUTIVE_TOKEN")

        self.director_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + CASTING_DIRECTOR
        }
        self.assistant_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + ASSISTANT_DIRECTOR
        }
        self.executive_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + EXECUTIVE_TOKEN
        }

#---------------------- GET MOVIES ----------------------
    def test_get_actors_ca(self):
        res = self.client().get('/actors', headers=self.assistant_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['actors'])

    def test_get_actors_cd(self):
        res = self.client().get('/actors', headers=self.director_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['actors'])

    def test_get_actors_ed(self):
        res = self.client().get('/actors', headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['actors'])

#----------------- GET MOVIES ------------------

    def test_get_movies_ca(self):
        res = self.client().get('/movies', headers=self.assistant_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['movies'])

    def test_get_movies_cd(self):
        res = self.client().get('/movies', headers=self.director_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['movies'])

    def test_get_movies_ed(self):
        res = self.client().get('/movies', headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['movies'])

#-------------- POST ACTORS ---------------
    def test_post_actor_ca(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }
        res = self.client().post('/actors', json=actor, headers=self.assistant_headers)
        #data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        #self.assertTrue(data['actor'])
        #actor_id = data['actor']['id']
        #db_actor = Actor.query.get(int(actor_id))
        #db_actor.delete()

    def test_post_actor_cd(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }
        res = self.client().post('/actors', json=actor, headers=self.director_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['actor'])
        actor_id = data['actor']['id']
        db_actor = Actor.query.get(int(actor_id))
        db_actor.delete()

    def test_post_actor_ed(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }
        res = self.client().post('/actors', json=actor, headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['actor'])
        actor_id = data['actor']['id']
        db_actor = Actor.query.get(int(actor_id))
        db_actor.delete()

    def test_post_actor_invalid_name(self):
        actor = {
            'name': '',
            'age': 46,
            'gender': 'M'
        }
        res = self.client().post('/actors', json=actor, headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')

# ------------------------- POST MOVIES ---------------------------------
    
    def test_post_movie_ca(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }

        res = self.client().post('/movies', json=movie, headers=self.assistant_headers)
        #data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        #self.assertTrue(data['movie'])
        #movie_id = data['movie']['id']
        #db_movie = Movie.query.get(int(movie_id))
        #db_movie.delete()
    
    def test_post_movie_cd(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }

        res = self.client().post('/movies', json=movie, headers=self.director_headers)
        #data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        #self.assertTrue(data['movie'])
        #movie_id = data['movie']['id']
        #db_movie = Movie.query.get(int(movie_id))
        #db_movie.delete()
    
    def test_post_movie_ed(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }

        res = self.client().post('/movies', json=movie, headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['movie'])
        movie_id = data['movie']['id']
        db_movie = Movie.query.get(int(movie_id))
        db_movie.delete()

    def test_post_movie_invalid_title(self):
        movie = {
            'title': '',
            'release_date': 2001,
        }

        res = self.client().post('/movies', json=movie, headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')

# -------------------- UPDATE ACTORS ------------------

    def test_update_actor_ca(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }
        res = self.client().post('/actors', json=actor, headers=self.assistant_headers)
        #post_data = json.loads(res.data)
        #actor_id = post_data['actor']['id']

        updated_actor = {
            'name': 'Mike',
            'age': 45,
            'gender': 'M'
        }

        res = self.client().patch(f'/actors/6', json=updated_actor, headers=self.assistant_headers)
        #updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 403)
        #self.assertTrue(updated_data['actor'])
        #self.assertEqual(updated_data['actor']['name'], 'Mike')
        #db_actor = Actor.query.get(int(updated_data['actor']['id']))
        #db_actor.delete()
    
    def test_update_actor_cd(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }
        res = self.client().post('/actors', json=actor, headers=self.director_headers)
        post_data = json.loads(res.data)
        actor_id = post_data['actor']['id']

        updated_actor = {
            'name': 'Mike',
            'age': 45,
            'gender': 'M'
        }

        res = self.client().patch(f'/actors/{actor_id}', json=updated_actor, headers=self.director_headers)
        updated_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(updated_data['actor'])
        self.assertEqual(updated_data['actor']['name'], 'Mike')
        db_actor = Actor.query.get(int(updated_data['actor']['id']))
        db_actor.delete()

    def test_update_actor_ed(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }
        res = self.client().post('/actors', json=actor, headers=self.executive_headers)
        post_data = json.loads(res.data)
        actor_id = post_data['actor']['id']

        updated_actor = {
            'name': 'Mike',
            'age': 45,
            'gender': 'M'
        }

        res = self.client().patch(f'/actors/{actor_id}', json=updated_actor, headers=self.executive_headers)
        updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertTrue(updated_data['actor'])
        self.assertEqual(updated_data['actor']['name'], 'Mike')
        db_actor = Actor.query.get(int(updated_data['actor']['id']))
        db_actor.delete()

    def test_update_actor_invalid_name(self):

        res = self.client().patch('/actors/500', headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')

# -------------------- UPDATE MOVIES --------------------

    def test_update_movie_ca(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }
        res = self.client().post('/movies', json=movie, headers=self.assistant_headers)

        #post_data = json.loads(res.data)
        #movie_id = post_data['movie']['id']

        updated_movie = {
            'title': 'Jumanji2',
            'release_date': 2005,
        }

        res = self.client().patch(f'/movies/5', json=updated_movie, headers=self.assistant_headers)
        #updated_data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        #self.assertTrue(updated_data['movie'])
        #movie_id = updated_data['movie']['id']
        #db_movie = Movie.query.get(int(movie_id))
        #db_movie.delete()

    def test_update_movie_cd(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }
        res = self.client().post('/movies', json=movie, headers=self.director_headers)

        #post_data = json.loads(res.data)
        #movie_id = post_data['movie']['id']

        updated_movie = {
            'title': 'Jumanji2',
            'release_date': 2005,
        }

        res = self.client().patch(f'/movies/6', json=updated_movie, headers=self.director_headers)
        #updated_data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        #self.assertTrue(updated_data['movie'])
        #movie_id = updated_data['movie']['id']
        #db_movie = Movie.query.get(int(movie_id))
        #db_movie.delete()

    def test_update_movie_ed(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }
        res = self.client().post('/movies', json=movie, headers=self.executive_headers)

        post_data = json.loads(res.data)
        movie_id = post_data['movie']['id']

        updated_movie = {
            'title': 'Jumanji2',
            'release_date': 2005,
        }

        res = self.client().patch(f'/movies/{movie_id}', json=updated_movie, headers=self.executive_headers)
        updated_data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(updated_data['movie'])
        movie_id = updated_data['movie']['id']
        db_movie = Movie.query.get(int(movie_id))
        db_movie.delete()

    def test_update_movie_invalid_title(self):
        res = self.client().patch('/movies/500', headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')

# ---------------- DELETE ACTORS ------------------------

    def test_delete_actor_ca(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }

        res = self.client().post('/actors', json=actor, headers=self.assistant_headers)
        #post_data = json.loads(res.data)

        #actor_id = post_data['actor']['id']
        #db_actor = Actor.query.get(actor_id)
        
        res = self.client().delete(f'/actors/9', headers=self.assistant_headers)
        #updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 403)
        #self.assertEqual(updated_data['success'], False)
        #self.assertEqual(updated_data['actor_id'], actor_id)


    def test_delete_actor_cd(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }

        res = self.client().post('/actors', json=actor, headers=self.director_headers)
        post_data = json.loads(res.data)
        actor_id = post_data['actor']['id']
        db_actor = Actor.query.get(actor_id)
        
        res = self.client().delete(f'/actors/{actor_id}', headers=self.director_headers)
        updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(updated_data['success'], True)
        self.assertEqual(updated_data['actor_id'], actor_id)

    def test_delete_actor_ed(self):
        actor = {
            'name': 'Michael',
            'age': 46,
            'gender': 'M'
        }

        res = self.client().post('/actors', json=actor, headers=self.executive_headers)
        post_data = json.loads(res.data)
        actor_id = post_data['actor']['id']
        db_actor = Actor.query.get(actor_id)
        
        res = self.client().delete(f'/actors/{actor_id}', headers=self.executive_headers)
        updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(updated_data['success'], True)
        self.assertEqual(updated_data['actor_id'], actor_id)

    def test_delete_actor_invalid_id(self):
        res = self.client().delete('/actors/500', headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')

    
    # -------------- DELETE MOVIES ------------------------

    def test_delete_movie_ca(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }

        res = self.client().post('/movies', json=movie, headers=self.assistant_headers)
        #post_data = json.loads(res.data)
        #movie_id = post_data['movie']['id']
        #db_movie = Movie.query.get(movie_id)
        
        res = self.client().delete(f'/movies/5', headers=self.assistant_headers)
        #updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 403)
        #self.assertEqual(updated_data['success'], True)
        #self.assertEqual(updated_data['movie_id'], movie_id)

    def test_delete_movie_cd(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }

        res = self.client().post('/movies', json=movie, headers=self.director_headers)
        #post_data = json.loads(res.data)
        #movie_id = post_data['movie']['id']
        #db_movie = Movie.query.get(movie_id)
        
        res = self.client().delete(f'/movies/4', headers=self.director_headers)
        #updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 403)
        #self.assertEqual(updated_data['success'], True)
        #self.assertEqual(updated_data['movie_id'], movie_id)

    def test_delete_movie_ed(self):
        movie = {
            'title': 'Jumanji',
            'release_date': 2001,
        }

        res = self.client().post('/movies', json=movie, headers=self.executive_headers)
        post_data = json.loads(res.data)
        movie_id = post_data['movie']['id']
        db_movie = Movie.query.get(movie_id)
        
        res = self.client().delete(f'/movies/{movie_id}', headers=self.executive_headers)
        updated_data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(updated_data['success'], True)
        self.assertEqual(updated_data['movie_id'], movie_id)

    def test_delete_movie_invalid_id(self):
        res = self.client().delete('/movies/500', headers=self.executive_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found')


if __name__ == '__main__':
    unittest.main()