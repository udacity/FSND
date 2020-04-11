# Full Stack API Final Project

## Full Stack Trivia

This trivia app is a fun game you can play for yourself or share with your family or friends.  It is capable of performing the tasks below:

1) Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer. 
2) Delete questions.
3) Add questions and require that they include question and answer text.
4) Search for questions based on a text query string.
5) Play the quiz game, randomizing either all questions or within a specific category. 

This project will give the ability to structure plan, implement, and test an API - skills essential for enabling future applications to communicate with others. 

## Getting Started

### Pre-requisite and Local Development

The development code can be found on the Github [project repository](https://github.com/opcreek/FSND/tree/master/projects/02_trivia_api/starter).

### Backend

The `./backend` directory contains the Flask and SQLAlchemy server.  To run the api, run the following commands from the backend directory:

```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

### Frontend

The `./frontend` directory contains a complete React frontend to consume the data from the Flask server.  To start the client, run the following command from the frontend directory:

```
npm start
```

### Tests

To run the tests, navigate to the backend folder and run the following commands:

```
createdb trivia_test
psql: trivia_test < trivia.psql
python test_flaskr.py
```

## API Referrence

### Getting Started

- Base URL: This app can only be run locally.  The backend app is hosted at http://127.0.0.1:5000.
- Authentication: This app do not require any authentication.

### Error Handling

The api will return the following 3 types of errors when request fails:

- 404: Resource Not Found
```
    {
          "success": False,
          "error": 404,
          "message": "resource not found"
    }
```

- 422: Unprocessable
```
    {
          "success": False,
          "error": 422,
          "message": "unprocessable"
    }
```

- 400: Bad Request
```
    {
          "success": False,
          "error": 400,
          "message": "bad request"
    }
```

## Endpoints

### GET /categories

- This endpoint handles GET requests for all available categories.

### GET /questions

- This endpoint handles GET requests for questions, including pagination per 10 questions.  This endpoint will return a list of questions, number of total questions and list of categories.


### DELETE /questions/\<int:id>

- This endpoint will delete a question using the question ID.

### POST /questions

- This endpoint will allow for posting a new question including the requirements for the answer text, category and difficulty score.

### POST /questions/search

- This endpoint will search for all questions based on a search term.  This endpoint will return any questions which contain the string specified in the search term.  It is also case-insensitive.

### GET /categories/\<int:id>/questions

- This endpoint will get all questions based on a category.  If needed, the results will also be paginated with 10 questions per page.

### POST /quizzes

- This endpoint will get questions to play the trivia.  This endpoint will return a random question within the given category if provided or for all categories.  This endpoint also has the capability to make sure that the current selection is not the previous questions used.


## Deployment: N/A

## Author

Renante Ramas

