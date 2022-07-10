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


Tests: (test_app.py)

One test for success behavior of each endpoint
One test for error behavior of each endpoint
At least two tests of RBAC for each role
