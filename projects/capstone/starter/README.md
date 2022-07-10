The Casting Agency models a company that is responsible for creating movies and managing and assigning actors to those movies.

To run the server:
1. source setup.sh
2. export FLASK_APP=app.py
3. export FLASK_ENV=development
4. flask run

Models: (models.py)

Movies with attributes title and release date
Actors with attributes name, age and gender

Endpoints: (app.py)

GET:     /actors
         /movies
DELETE:  /actors/<actor_id>
POST:    /actors 
PATCH:   /actors/<actor_id>

Roles & Permissions:

1. Casting Assistant: Can view actors and movies <get:actors and get:movies>

2. Casting Director: All permissions a Casting Assistant has and can add or delete an actor from the database and modify actors or movies <get:actors ,get:movies, post:actors, patch:actors, delete:actors>

JWT Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRmdjZaUTNwZEpvLXNlRUJ0RERiRiJ9.eyJpc3MiOiJodHRwczovL2Rldi1nYXJ2aXRhLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwODY4MDQzNzczMDI2NzcwMTg4MiIsImF1ZCI6ImNhc3RpbmdfYWdlbmN5IiwiaWF0IjoxNjU3NDM3NzQ1LCJleHAiOjE2NTc0NDQ5NDUsImF6cCI6ImhwMFhVOHljdTVCRzA0OFNBMmQ5TGRPSFpFQ2p2UkhnIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3IiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9yIiwicG9zdDphY3RvcnMiXX0.i5zdiABCfUcd-4XPrgvq3lbgrvuWF5ZbcwsmFC3tKGqrPZjPsQPqZRKf5VAr1Z8U8ftK9HbWXKuV26Wont34r8ui_VPwboZXYJMi8n61giEup2vAlcXdUPVY8Ylz_wq_-FwkaRFAICSijhTbyGFUyezO9WI-KmcXCl6-yVzXyESPo5c9trGrdFTkyp8dIdmQvzasjKbJwvIVpEBoF8s16ce2nnj4bGZyZxGalvchwGJAKStnNfzCo9pm0jamD6ji84mjkMvk_zT9faeKVrGTVEFvOLD0hvvAUt5g0n7HgvnxAXC5ycLjC9jAiH6BFa8_B8sySiH3O1khWXJV77HgHw


Tests:

One test for success behavior of each endpoint
One test for error behavior of each endpoint
At least two tests of RBAC for each role
