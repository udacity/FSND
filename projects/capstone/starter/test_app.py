import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie

ca_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkE2UU1saTh3UWp1a2ZaWjhzbHpmdiJ9.eyJpc3MiOiJodHRwczovLzNkeS5hdXRoMC5jb20vIiwic3ViIjoiSlc3WDVOb29FYVNHQWxkaXpINEYxNFNSM2dQOEZlaW5AY2xpZW50cyIsImF1ZCI6Im1vdmllcyIsImlhdCI6MTU4ODg2MzkzOSwiZXhwIjoxNTg4OTUwMzM5LCJhenAiOiJKVzdYNU5vb0VhU0dBbGRpekg0RjE0U1IzZ1A4RmVpbiIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIl19.nFj_9xhMEbjx7g7d01rITTTJrzuWtBO7WWHqffQtpyabbs3-2N7jA4Ij7hhEUkz1yXGJyxpjSZouN5PDAZfQN3x3HG4A_5vW3Uo1XQX8rv3ylhAElcSEenKpUjE3_260i4X5Ehh_vFzDFmuWK2TEEHJN2D2D0vJaJ-FPHQJKvOcTK8H_tCV7CQvlkg-g-osL1QmGMSeoqDQcqVtFLpV1kPRc-WxJiBSjAeQh0wGBgwA4d-Cwsb2QBSB5KRmLlJt47zy_enx_MH6XVg0q6iz7gnQhDiVqiES9KeT_S49_0vejINstXAO2FjFaROCv9YEfLX6qYKu9DxsiFd_wFI-Jzw'
cd_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkE2UU1saTh3UWp1a2ZaWjhzbHpmdiJ9.eyJpc3MiOiJodHRwczovLzNkeS5hdXRoMC5jb20vIiwic3ViIjoiSlc3WDVOb29FYVNHQWxkaXpINEYxNFNSM2dQOEZlaW5AY2xpZW50cyIsImF1ZCI6Im1vdmllcyIsImlhdCI6MTU4ODg2MjU4NiwiZXhwIjoxNTg4OTQ4OTg2LCJhenAiOiJKVzdYNU5vb0VhU0dBbGRpekg0RjE0U1IzZ1A4RmVpbiIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMgcG9zdDphY3RvcnMgZGVsZXRlOmFjdG9ycyBwYXRjaDphY3RvcnMgcGF0Y2g6bW92aWVzIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwicGVybWlzc2lvbnMiOlsicmVhZDphY3RvcnMiLCJyZWFkOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwiZGVsZXRlOmFjdG9ycyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyJdfQ.SUM79IJa44CehFVby5ckj-9OdyqJDTKgnfnsf7YBJ1TxmHVb-gexJFDaV40ZEdZvBHFDmxEbDT6tFX2IY3LHv7D1rG5adb9kTBza-gYJ74DsbogLc-jYNCWw2deCXr5Ke8awxynYw6oNmpktk4Dky6EBCPDOm_KyuqMgqZ7hUUvAwu5YV0xfVcIMz0JiICVeDhPcL3mnCa7nab54CUxVdMR5Hl8bxnZlRNY4w5t-O8pGrjhxlPmHiKTum9F8ZEFwqIz8mtysqhTAEdp1OWY2X9NOK8pnpRdflHf7xPIFMBGdaiwZbIzn-MLKHIbfUlzKEF1SAmKFPnuQ2abmHhIjoQ'
ep_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkE2UU1saTh3UWp1a2ZaWjhzbHpmdiJ9.eyJpc3MiOiJodHRwczovLzNkeS5hdXRoMC5jb20vIiwic3ViIjoiSlc3WDVOb29FYVNHQWxkaXpINEYxNFNSM2dQOEZlaW5AY2xpZW50cyIsImF1ZCI6Im1vdmllcyIsImlhdCI6MTU4ODg2Mzk4NCwiZXhwIjoxNTg4OTUwMzg0LCJhenAiOiJKVzdYNU5vb0VhU0dBbGRpekg0RjE0U1IzZ1A4RmVpbiIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMgcG9zdDptb3ZpZXMgcG9zdDphY3RvcnMgZGVsZXRlOm1vdmllcyBkZWxldGU6YWN0b3JzIHBhdGNoOmFjdG9ycyBwYXRjaDptb3ZpZXMiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIiwicG9zdDptb3ZpZXMiLCJwb3N0OmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJkZWxldGU6YWN0b3JzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIl19.BJ_Ia4H2p3GoVthPFAV8KbFpUjrzCcR23dENGx35x1n7cu20oTA6E9WHrphhmHHXpbTcOxlryUrwGOfZ4lcNYnW5SdUIST6Wz65rfMiD0TefcA5rNU0EtfWtLSZilQo9f8ADxumHWxPYcQPYqRJu-zYNVJFVGwgJJx1gKjcSeDOnWetBJQG2ThZ4O2iv2Sz3HzfQYHi1dxY8ELB_bkn2Ptq1Rxrg3VCe_bpXHupdgyEQsitwg9sSO2d4yvTrs1wE7NXxFDxe65cioTXVgVqlMElPDsJPRjS3TMBEZiJdbW5UF4pHDC0QCBhb2PQWbsw8wHK36iWp1KhmDWp2TwmS9w'


class ActorsMoviesTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "actors_movies_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_actor = {
            'name': 'Jim Carey',
            'age': '58',
            'gender': 'male'
        }

        self.new_movie = {
            'title': 'The Matrix',
            'release_date': 'March 31, 1999'
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

    def test_get_actors(self):
        res = self.client().get('/actors', headers={"Authorization": "Bearer {}".format(ca_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor_list'])
        self.assertTrue(data['number_of_actors'])

    def test_get_movies(self):
        res = self.client().get('/movies', headers={"Authorization": "Bearer {}".format(ca_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # self.assertTrue(data['movie_list'])
        self.assertTrue(data['number_of_movies'])

    # Casting Assistant unauthorized attempt to post to actors

    def test_ca_post_to_actors_unauthorized(self):
        res = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(ca_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    # Casting Assistant unauthorized attempt to post to movies

    def test_ca_post_to_movies_unauthorized(self):
        res = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(ca_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    # Casting Director

    def test_cd_post_to_actors(self):
        res = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(cd_token)},
                                 json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor_list'])
        self.assertTrue(data['created_id'])
        self.assertTrue(data['number_of_actors'])

    def test_cd_delete_to_no_actors(self):
        res = self.client().delete(f'/actors/1000', headers={"Authorization": "Bearer {}".format(cd_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_cd_delete_to_actors(self):
        insert_res = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(cd_token)},
                                        json=self.new_actor)
        insert_data = json.loads(insert_res.data)
        actor_id = insert_data['created_id']

        res = self.client().delete(f'/actors/{actor_id}', headers={"Authorization": "Bearer {}".format(cd_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['number_of_actors'])

    def test_cd_patch_to_actors(self):
        insert_res = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(cd_token)},
                                        json=self.new_actor)
        insert_data = json.loads(insert_res.data)
        actor_id = insert_data['created_id']

        res = self.client().patch(f'/actors/{actor_id}', headers={"Authorization": "Bearer {}".format(cd_token)},
                                  json={
                                      "name": "Derek",
                                      "gender": "male"
                                  })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'])

    def test_cd_patch_to_movies(self):
        insert_res = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(ep_token)},
                                        json=self.new_movie)
        insert_data = json.loads(insert_res.data)
        movie_id = insert_data['created_id']

        res = self.client().patch(f'/movies/{movie_id}', headers={"Authorization": "Bearer {}".format(cd_token)},
                                  json={
                                      "title": "The MATRIX"
                                  })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])

    def test_cd_post_to_movies_unauthorized(self):
        res = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(cd_token)},
                                 json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_cd_delete_to_movies_unauthorized(self):
        res = self.client().delete('/movies/1', headers={"Authorization": "Bearer {}".format(cd_token)},
                                   json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_ep_post_to_movies(self):
        res = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(ep_token)},
                                 json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie_list'])
        self.assertTrue(data['created_id'])
        self.assertTrue(data['number_of_movies'])

    def test_ep_delete_to_movies(self):
        insert_res = self.client().post('/movies', headers={"Authorization": "Bearer {}".format(ep_token)},
                                        json=self.new_movie)
        insert_data = json.loads(insert_res.data)
        movie_id = insert_data['created_id']
        print(movie_id)

        res = self.client().delete(f'/movies/{movie_id}', headers={"Authorization": "Bearer {}".format(ep_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['number_of_movies'])

    def test_ep_delete_to_no_movies(self):
        res = self.client().delete(f'/movies/1000', headers={"Authorization": "Bearer {}".format(ep_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
