# Full Stack Trivia API Backend

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

to run the test suite, you'll need to create a test db with a user with SUPER privilegs named `trivia_test_user` and then run `psql trivia_test < trivia_test.psql` to set up the test db

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

## API Documentation
```

Endpoints (base url = '/api/ + {endpoint_url}')

GET '/categories'
- Fetches all categories
- Request Arguments: None
- Returns: An object with a single key, categories
- Example: 
    {'1': "Science",
    '2': "Art",
    }

GET '/questions'
- Fetches all questions
- Request Arguments: page (optional)
- Returns: JSON with the following keys
-- questions = list of all questions
-- total_questions = count of all questions in db
-- categories = list of all categories
-- current_category = current_category for questions
- Example: [{
        "id":5,
        "question":"Whose autobiography is entitled 'I know why the caged bird sings?'",
        "answer":"Maya Angelou",
        "difficulty":2,
        "category":4
        }
    ]

POST '/questions/'
- Retrieve question(s) based on query
- Request Arguments: none
- Request Body:
-- [{"searchTerm": "example"}]
- Returns: An object with single key, Questions, and a list of questions that match the searchTerm
- Example: [{
    "questions": [{
        "id": 19,
        "question": "what is my favorite color",
        "answer": "blue"
    }]
}]

GET '/categories/<int:category_id>/questions'
- Retrieves all questions given a category_id
- Request Arguments: category_id
- Returns: list of all questions for the given category as JSON 
-- questions = list of all questions
-- total_questions = count of all questions in db
-- categories = list of all categories
-- current_category = current_category for questions

DELETE '/questions/<int:question_id>'
- Deletes a question by id
- Request Arguments: question_id
- Returns: 204 on successful deletion


POST '/questions/create/'
- Creates a new question
- Request Args: none
- Request Body: JSON with Question key:value pairs
- Returns: 201 on success with Question key:value pairs as JSON

POST '/quizzes'
- Returns data needed to play the game/quiz
- Request Args: none
- Request Body: JSON with key:value pairs
-- previous_questions: []
-- quiz_category: {}
- Returns: key:value pairs as JSON

```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia_test.psql
python3 test_flaskr.py
```

If you are getting an error when creating the db you probably forgot to create the trivia_test_user with the correct privileges
