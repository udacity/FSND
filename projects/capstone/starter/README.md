# Full Stack Nanodegree Capstone Project

## Background

This project showcases many of the skills I've learned through the Udacity Full Stack Nanodgree curriculum. This entire api has been built from the ground up with no starter code. 

## Getting Started

This code is currently deployed on Heroku and accessible at the following URL.

    https://derek-y-fsnd-capstone-app.herokuapp.com
    
## Local Quick Start

###Prepare your enviornment and app

Start Postgresql

* install postgres if needed
* create a database
* save the database, username, and password someplace handy

####Clone the repository
```bash
https://github.com/derek-yesmunt/FSND/tree/master/projects/capstone/starter
```

####Update the models.py
Update the database name and configure the database path with username and password if you have one.


## Running the server
From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `app.py` directs flask to use the `app.py` file as the application. 

### Roles and Permissions

There are three roles with different permissions setup for this api:

Casting Assistant

- Can view actors and movies

Casting Assistant Authentication Token
```bash
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkE2UU1saTh3UWp1a2ZaWjhzbHpmdiJ9.eyJpc3MiOiJodHRwczovLzNkeS5hdXRoMC5jb20vIiwic3ViIjoiSlc3WDVOb29FYVNHQWxkaXpINEYxNFNSM2dQOEZlaW5AY2xpZW50cyIsImF1ZCI6Im1vdmllcyIsImlhdCI6MTU4OTMyNDA5NywiZXhwIjoxNTg5NDEwNDk3LCJhenAiOiJKVzdYNU5vb0VhU0dBbGRpekg0RjE0U1IzZ1A4RmVpbiIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIl19.X9_mL8aI2u5bM88fJVGQPNE7ueD5S1dCJ2Q5JIBPDjxhZluI8M5_ihhF3O_RtuDBUBaXwDjdri91zdOFSp0aVeQrUEIAUTG9jL8iTCWRuNaDBO2GsmA2fSfLJc8xY7sxM1XHk6lEcs3aOfVQTZeVE39fFfuSHbOUNNDI9-5Ra1x-umRqRfLScYlQ2AGtkZpamrjF3Qk3bfvmLxe4ShMgIQJi_XhfLsQG5LemUsZjY7n_K--2R_6Lwf9xWLZXP1_7WeHS2l2VK_1nNeE0mvpVd-BOUf6bv5N7ZSoKBIg8dliHIuQ96Np9TGG_aVK9YSQddi1K9xI8Z70OxavdX5dXyg
```

Casting Director

- All permission a Casting Assitant has and..
- Add or delete an actor from the database
- Modify actors or movies

Casting Director Authentication Token
```bash
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkE2UU1saTh3UWp1a2ZaWjhzbHpmdiJ9.eyJpc3MiOiJodHRwczovLzNkeS5hdXRoMC5jb20vIiwic3ViIjoiSlc3WDVOb29FYVNHQWxkaXpINEYxNFNSM2dQOEZlaW5AY2xpZW50cyIsImF1ZCI6Im1vdmllcyIsImlhdCI6MTU4OTMyNDA1MCwiZXhwIjoxNTg5NDEwNDUwLCJhenAiOiJKVzdYNU5vb0VhU0dBbGRpekg0RjE0U1IzZ1A4RmVpbiIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMgcG9zdDphY3RvcnMgZGVsZXRlOmFjdG9ycyBwYXRjaDphY3RvcnMgcGF0Y2g6bW92aWVzIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwicGVybWlzc2lvbnMiOlsicmVhZDphY3RvcnMiLCJyZWFkOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwiZGVsZXRlOmFjdG9ycyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyJdfQ.2Gn13pe6qSBQuxjK-gAIrkhTNb5os7u1Rdcqh2oSQdfjD0d54Gg95MKMJArSUGOgOYkZnz49geRBeUO7SQMTzyxBvXuM98Spl01--rkiwmcfhEkUGcqG3bUajD_X63LH6mtGXNmExlv-bQ1_pKak_diLk4Dz3cirLSRh85-10obtakEaLaH56v0qIAg4zyn-zL3J_4kwPgG76Alo1dJ_LCYS19quUomqzvPfRtfmEKiku4hcPV7PS5yzTYHfK97IeJO8IUGwbWsAnDzXruNtvxh0mKhkhkK2IcisQKeaLLApmVl870CFXzdb5XE8L4gJRIZ-Koq7kGB9bo0ChlymVg
```

Executive Producer

- All permissions a Casting Director has and...
- Add or delete a movie from the database

Executive Producer Authentication Token
```bash
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkE2UU1saTh3UWp1a2ZaWjhzbHpmdiJ9.eyJpc3MiOiJodHRwczovLzNkeS5hdXRoMC5jb20vIiwic3ViIjoiSlc3WDVOb29FYVNHQWxkaXpINEYxNFNSM2dQOEZlaW5AY2xpZW50cyIsImF1ZCI6Im1vdmllcyIsImlhdCI6MTU4OTMyMzk5MCwiZXhwIjoxNTg5NDEwMzkwLCJhenAiOiJKVzdYNU5vb0VhU0dBbGRpekg0RjE0U1IzZ1A4RmVpbiIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMgcG9zdDptb3ZpZXMgcG9zdDphY3RvcnMgZGVsZXRlOm1vdmllcyBkZWxldGU6YWN0b3JzIHBhdGNoOmFjdG9ycyBwYXRjaDptb3ZpZXMiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIiwicG9zdDptb3ZpZXMiLCJwb3N0OmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJkZWxldGU6YWN0b3JzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIl19.sx88kFiBHhs0MleDgyYermnJwTP-qh_6yMBxM_nKt7UtDUHv2iogx3CDf32N-B5JaiaaqbC8Ls5n8TkBT51Z9WbCUFAt0bnn9qOc6MeT5TMiFiQS2172I53nfq3CnrTseg5sz_mKW6pgMbiCYL7p5Ydhxr5P0RwqTKQXic2Mghfr9sFV8r2vsrjwLcD7uzXp68MBSS2H5f131M9mEg0bQv-UrQb52Fa5I0u3Ln7BSx86slsPwyFZdPPfoW2AfTFuGC8ErJp9GZCJnAN3oOmSbxfWPqjfwiLevcybNz9c9YNvCFHGj1MQmuZvXbZ92M_PaVyy-_6Pfeb3MBUlmr5xjg
```

## Resource endpoint library

Endpoints

- GET '/movies'
- GET '/actors'
- POST '/movies'
- POST '/actors'
- DELETE '/movies/<int:movie_id>'
- DELETE '/actors/<int:actor_id>'
- PATCH '/movies/<int:movie_id>'
- PATCH '/actors/<int:actor_id>'

GET '/movies' 

- Fetches an list of movies with "title" and "release_date" key values.
- Returns:
    - Success value
    - Status code
    - The number of movies in the database

```bash
{
    "movie_list": [
        {
            "id": 4,
            "release_date": "Mon, 31 Mar 1999 00:00:00 GMT",
            "title": "The Matrix"
        },
        {
            "id": 3,
            "release_date": "Fri, 16 Feb 1999 00:00:00 GMT",
            "title": "Happy Gilmore"
        }
    ],
    "number_of_movies": 2,
    "status_code": 200,
    "success": true
}
```

GET '/actors' 

- Fetches an list of actors with "name", "age", "gender" and "id" key values
- Returns:
    - Success value
    - Status code
    - The number of actors in the database

```bash
{
    "actor_list": [
        {
            "age": 63,
            "gender": "Male",
            "id": 1,
            "name": "Tom Hanks"
        },
        {
            "age": 47,
            "gender": "female",
            "id": 3,
            "name": "Gwyneth Paltrow"
        }
    ],
    "number_of_actors": 2,
    "status_code": 200,
    "success": true
}
```

POST '/movies'

- Creates a new movie with given "title" and "release_date"
- Returns:
    - Success value
    - Created id
    - Movie list
    - Number of movies in the database

```bash
{
    "created_id": 2,
    "movie_list": [
        {
            "id": 2,
            "release_date": "Mon, 15 Mar 1999 00:00:00 GMT",
            "title": "The Matrix"
        }
    ],
    "number_of_movies": 1,
    "success": true
}
```

POST '/actors'

- Creates a new actor with given "name", "age", and "gender"
- Returns:
    - Success value
    - Created id
    - Actor list
    - Number of actors in the database

```bash
{
    "created_id": 3,
    "actor_list": [
        {
            "age": 63,
            "gender": "Male",
            "id": 1,
            "name": "Tom Hanks"
        },
        {
            "age": 47,
            "gender": "female",
            "id": 3,
            "name": "Gwyneth Paltrow"
        }
    ],
    "number_of_actors": 2,
    "status_code": 200,
    "success": true
}
```

DELETE '/movies/<int:movie_id>'

- Deletes a movie with a given id
- Returns:
    - Success value
    - Status code
    - Number of movies in the database

```bash
{
    "number_of_movies": 1,
    "status_code": 200,
    "success": true
}
```

DELETE '/actors/<int:actor_id>'

- Creates a new actor with given "name", "age", and "gender"
- Returns:
    - Success value
    - Created id
    - Actor list
    - Number of actors in the database

```bash
{
    "created_id": 3,
    "actor_list": [
        {
            "age": 63,
            "gender": "Male",
            "id": 1,
            "name": "Tom Hanks"
        },
        {
            "age": 47,
            "gender": "female",
            "id": 3,
            "name": "Gwyneth Paltrow"
        }
    ],
    "number_of_actors": 2,
    "status_code": 200,
    "success": true
}
```

PATCH '/movies/<int:movie_id>'

- Updates a movie with a given id and any included values for "title" or "release_date"
- Returns:
    - Success value
    - Status code
    - Updated data for that movie

```bash
{
    "movie":{
        "title": "THE MATRIX",
        "release_date": "Mon, 15 Mar 1999 00:00:00 GMT"
    },
    "status_code": 200,
    "success": true
}
```
PATCH '/actors/<int:actor_id>'

- Updates a actor with a given id and any included values for "title" or "release_date"
- Returns:
    - Success value
    - Status code
    - Updated data for that actor

```bash
{
    "actor": {
        "age": 28,
        "gender": "male",
        "id": 3,
        "name": "Derek"
    },
    "status_code": 200,
    "success": true
}
```

### Errors Handled

Errors that will be handled are:

- 422 - Unprocessable
- 404 - Resource not found
- 401 - Unauthorized

Errors will include a success value, message, and error value.

Example error response
```bash
{
    "error": 401,
    "message": "token_expired",
    "success": false
}

```