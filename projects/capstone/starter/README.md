# Casting Agency API Backend

## Description

This project demonstrates the backend of a simple casting agency, a company that is responsible for creating movies, managing and assigning actors to those movies. The backend is designed to work for three types of users: Casting Assistants, Casting Directors and Executive Producers. Some general informtion about which movies have which actors can be viewed by public users. The project is created as a demo to show how casting agencies work. 

Casting Assistants can view information about actors and movies. A Casting Director has all permissions a Casting Assistant has and permissions to modify actors and movies as well as add and delete actors. An Executive Producer has all the permissoins a Casting Director has and permissions to add or delete movies. Users must be authorized to be able to perform role-based requests to the backend via API described below.

Authorization of users is enabled via Auth0 in which three seperate roles (Casting Assistant, Casting Director and Executive Producer) have been created and assigned seperate permissions.

## Project Dependencies

The project depends on Python 3.x wihch we recommend to download and install from their official website and use a virtual environment to install all dependencies.


## PIP Dependencies
After having successfully installed Python, navigate to the root folder of the project (the project must be forked to your local machine) and run the following in a command line:
```
pip3 install -r requirements.txt
```
This will install all the required packages to your virtual environment to work with the project.


## Database Setup
The models.py file contains connection information to the Postgres database, which must be setup and running. Provide a valid username and password if applicable.

1. Create a database with name Capstone using Psql CLI as shown below:
`create database capstone;`

2. Initiate and migrate the database with the following commands in command line:
```
flask db init
flask db migrate
flask db upgrade
```

This will create all necessary tables and relationships to work with the project.


## Data Modelling
The data model of the project is provided in models.py file in the root folder. The following schema for the database and helper methods are used for API behaviour:
There are three tables created: Actor, Movie and Casting.
The Actor table is used to store actors' information.
The Movie table is used to store movies' information.
The Casting talbe is used to store the many-to-many relationships between actors and movies.


## Running the Local Development Server
All necessary credential to run the project are provided in the setup.sh file. The credentials can be enabled by running the following command:
`source setup.sh`
To run the API server on a local development environment the following commands must be additionally executed:
### On Linux: export
```
export FLASK_APP=app.py
export FLASK_ENV=development
```
### On Windows: set
```
set FLASK_APP=app.py
set FLASK_ENV=development
```

### API Server

All accessable endpoints of the project are located in the app.py file.

Run the following command in the project root folder to start the local development server:
```
flask run
```

## RBAC Credentials and Roles
Auth0 was set up to manage role-based access control for three users. The API documentation below describes, among others, by which user the endpoints can be accessed. Access credentials and permissions are handled with JWT tokens which must be included in the request header.

### Permissions
Casting Assistants can access API endpoints that have the following permission requirements:
`'get:actors'` - get all actors' information
`'get:movies'` - get all movies' information

Casting Directors can access API endpoints that have the following permission requirements:
`'get:actors'` - get all actors' information
`'get:movies'` - get all movies' information
`'patch:actors'` - edit an actor by id
`'patch:movies'` - edit a movie by id
`'post:actors'` - create actors
`'delete:actors'` - remove an actor inforamtion by id

Casting Directors can access API endpoints that have the following permission requirements:
`'get:actors'` - get all actors' information
`'get:movies'` - get all movies' information
`'patch:actors'` - edit an actor by id
`'patch:movies'` - edit a movie by id
`'post:actors'` - create actors
`'post:movies'` - create movies
`'delete:actors'` - remove an actor inforamtion by id
`'delete:movies'` - remove an movie information by id
`'post:casting'` -  assign actors to movies

There are also publicly available endpoints that do not require authorization. This is done to ensure every user can see what movies include what actors and vice versa.

## API Endpoints

### Public Endpoints
#### GET '/'
- Access home page
- Request arguments: None
- Returns: success status

Sample curl request:
`curl -X GET http://127.0.0.1:5000/`

```
Sample response:
{
  "success": true
}
```


#### GET '/casting/movie_id'
- Fetches a list of actors who acted/will act in a movie by movie_id
- Request Arguments: None
- Returns: the success status, movie id and a list of actor names

Sample curl request: 
`curl -X GET http://127.0.0.1:5000/casting/1`

Sample response:
```
{
"actors":["King","Queen"],
"movie_id":1,
"success":true
}
```

### Endpoints accessable with Authorization
#### GET '/actors'
- Fetches a list of actors information including name, age and gender
- Request Arguments: None
- Returns: A JSON object with two keys: 'scucess' and 'actors'

Sample curl request:
`curl -H "Authorization: $casting_director" -X GET http://127.0.0.1:5000/actors`

Sample curl response:
```
{
  "actors": [
    [
      1,
      "King",
      "100",
      "M"
    ],
    [
      2,
      "Queen",
      "110",
      "F"
    ]
  ],
  "success": true
}
```

#### GET '/movies'
- Fetches a list of movies information including title and release date
- Request Arguments: None
- Returns: A JSON object with two keys: 'scucess' and 'movies'

Sample curl request:
`curl -H "Authorization: $casting_director" -X GET http://127.0.0.1:5000/movies`

Sample curl response:
```
{
  "movies": [
    [
      1,
      "Lion King",
      "2/10/2020"
    ],
    [
      2,
      "Animal World",
      "2/10/2022"
    ]
  ],
  "success": true
}
```


#### DELETE '/actors/<int:actor_id>'
- Deletes an actor by actor id
- Request arguments: None
- Returns: a JSON object with success status and the deleted actor id by this request

Sample curl request:
`curl -H "Authorization: $executive_producer" -X DELETE http://127.0.0.1:5000/actors/3`

Sample response:
`{"delete":3,"success":true}`

#### DELETE '/movies/<int:movie_id>'
- Deletes a movie by movie id
- Request arguments: None
- Returns: a JSON object with success status and the deleted movie id by this request

Sample curl request:
`curl -H "Authorization: $executive_producer" -X DELETE http://127.0.0.1:5000/movies/3`

Sample response:
`{"delete":3,"success":true}`


#### POST '/actors/add'
- Creates an actor profile in database
- Request arguments: a JSON or Form formatted object including actor information
- Returns: the actor that was created by this request successfully
Sample curl request:
`curl -d '{"name":"King", "age":"100", "gender":"M"}' -H "Content-Type: application/json" -H "Authorization: $casting_director" -X POST http://127.0.0.1:5000/actors/add`
Sample response: 
```
{
  "add": {
    "age": "100",
    "gender": "M",
    "name": "King"
  },
  "success": true
}
```


#### POST '/movies/add'
- Creates a movie in database
- Request arguments: a JSON or Form formatted object including movie title and release data
- Returns: the movie that was created by this request successfully
Sample curl request:
`curl -d '{"title":"Lion King", "release_date":"2/10/2020"}' -H "Content-Type: application/json" -H "Authorization: $executive_producer" -X POST http://127.0.0.1:5000/movies/add`
Sample response:
```
{
  "add": {
    "release_date": "2/10/2020",
    "title": "Lion King"
  },
  "success": true
}
```


#### POST '/casting/add'
- Assigns an actor to a movie
- Request arguments: a JSON object with movie id and actor id
- Returns: a JSON object with success status and the information just added to database by this request

Sample curl request: 
`curl -d '{"movie_id":1, "actor_id":1}' -H "Content-Type: application/json" -H "Authorization: $executive_producer" -X POST http://127.0.0.1:5000/casting/add`

Sample response:
```
{
  "add": {
    "actor": 1,
    "movie": 1
  },
  "success": true
}
```


#### PATCH '/actors/<int:actor_id>'
- Updates an actor information by id
- Request arguments: a JSON or form formatted object with name, age and gender information
- Returns: a JSON object with success status and actor id what was updated by this request

Sample curl request:
`curl -d '{"name": "King", "age": "30", "gender": "M"}' -H "Content-Type: application/json" -H "Authorization: $executive_producer" -X PATCH http://127.0.0.1:5000/actors/1`

Sample response:
```
{
  "success": true,
  "update": 1
}
```


#### PATCH '/movies/<int:movie_id>'
- Updates a movie information by id
- Request arguments: a JSON or form formatted object with title and release date
- Returns: a JSON object with success status and movie id what was updated by this request

Sample curl request:
`curl -d '{"title": "Tiger King", "release_date": "2/2/2020"}' -H "Content-Type: application/json" -H "Authorization: $executive_producer" -X PATCH http://127.0.0.1:5000/movies/1`

Sample response:
```
{
  "success": true,
  "update": 1
}
```

## Testing
The testing of all endpoints was implemented with unittest. Each endpoint can be tested with one success test case and one error test case. RBAC feature can also be tested. All test cases are stored in test_app.py in the project root folder.

In the command line run the test file:
`python test_app.py`

## Heroku Deployment and Base URL
https://capstone-app-lili.herokuapp.com/






