# Full Stack Trivia API Backend

This project is invested in fostering the bonding experience for Udacity's employees and students. Some team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience was limited and wasn't built out, thanks to this, we now have a fully fledged out API built to meet the needs of a growing community looking to remain connected.

## Getting Started

### Installing Dependencies

Navigate to your backend directory.

```sh
cd starter/backend/
```

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virtual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

Activate your virtual environment if you havent by running the below.

```sh
virtualenv --no-site-packages env
source env/bin/activate
```

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```sh
pip3 install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) iis an extension that handles SQLAlchemy database migrations for Flask applications using Alembic.

## Database Setup

Start by running

```sh
flask db upgrade
```

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```sh
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```sh
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.

Note: All backend code follows [PEP8 style guidelines.](https://www.python.org/dev/peps/pep-0008/)

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle GET requests for all available categories.
4. Create an endpoint to DELETE question using a question ID.
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.
6. Create a POST endpoint to get questions based on category.
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422 and 500.

## API Documentation

- Base URL: Currently not hosted, when run locally it is hosted at the default `http://127.0.0.1:5000`, which is already set as a proxy in the Frontend application.
- Authentication: No authentication needed for this version

### Question resource endpoints

#### GET `/api/questions`

- Fetches questions, by default you get an array of the first 10 questions i.e page 1.
- Request Arguments: page/none, to get a certain page you can make use of the page query parameter as shown below, e.g sending page=2, will give you the second set of ten questions, questions 11 - 20.
- Response: An object containing a list of *questions*, the number of *total_questions*, *current_category*, list of *categories* and *success* message.
  
Sample Request

```sh
curl -H 'Content-Type: application/json' http://127.0.0.1:5000/api/questions?page=2
```

Sample Response

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History"...
  },
  "current_category": "All",
  "questions": [
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    }...
  ],
  "success": true,
  "total_questions": 19
}
```

#### DELETE `/api/questions/<question_id>`

- Deletes any question with id equals question_id from the database.
- Request Arguments: question_id. This refers to the id of the specific question to be deleted.
- Response: success or 404 if not found.

Sample Request

```sh
curl -X DELETE http://127.0.0.1:5000/api/questions/3
```

Sample Response

```sh
{
  'success': True
}
```

#### POST `/api/questions`

This Works as both a creation and a search endpoint for questions

##### Creating new questions

- Creates a new question using the given data.
- Response: object containing newly created question.

Sample Request

```sh
curl -X POST -d '{
    "question": "question",
    "answer": "answer",
    "category": 2,
    "difficulty": 3
  }' -H 'Content-Type: application/json' http://127.0.0.1:5000/api/questions
```

Sample Response

```sh
{
  "question": {
    "answer": "answer",
    "category": 2,
    "difficulty": 3,
    "id": 35,
    "question": "question"
  },
  "success": true
}
```

##### Search for question using searchTerm

- Used to get specific questions that match a searchTerm
- Response: Object containing a list of questions for whom the search term is a substring of its question, total_questions, and current_category

Sample Request

```sh
curl -X POST -d '{
  "searchTerm": "title"  
}' -H 'Content-Type: application/json' http://127.0.0.1:5000/api/questions
```

Sample Response

```sh
{
  "current_category": "All",
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "success": true,
  "total_questions": 2
}
```

#### GET `/api/categories/<int:category_id>/questions`

- Fetches a list of questions that have same category as category_id

Sample Request

```sh
curl -H 'Content-Type: application/json' http://127.0.0.1:5000/api/categories/1/questions
```

Sample Response

```sh
{
  "current_category": "Science",
  "questions": [
      {
          "answer": "The Liver",
          "category": 1,
          "difficulty": 4,
          "id": 20,
          "question": "What is the heaviest organ in the human body?"
          },
          {
          "answer": "Alexander Fleming",
          "category": 1,
          "difficulty": 3,
          "id": 21,
          "question": "Who discovered penicillin?"
      }
  ],
  "success": True,
  "total_questions": 2
}
```

#### POST `/api/quizzes`

- Fetch random quiz question that matches quiz_category and not a previous_question

NOTE: If questions in quiz_category have been exhausted and number of answered questions is not yet equal to questionsPerPlay, a random question from another category is returned

Sample Request

```sh
curl -X POST -d '{
  "quiz_category": {"type": "Science", "id": 1},
  "previous_questions": []
}' -H 'Content-Type: application/json' http://127.0.0.1:5000/api/quizzes
```

Sample Response

```sh
{
  "question": {
    "answer": "The Liver",
    "category": 1,
    "difficulty": 4,
    "id": 20,
    "question": "What is the heaviest organ in the human body?"
  },
  "success": true
}
```

### Category resource endpoints

#### GET `/api/categories`

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Response: An object with a single key, categories, that contains category id:type key:value pairs.

Sample Request

```sh
curl -H 'Content-Type: application/json' http://127.0.0.1:5000/api/categories
```

Sample Response

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true
}
```

#### Error Handling

Errors are returned in the following format:

```sh
{
  "sucess": False,
  "error": 400,
  "message": "bad_request
}
```

We have 5 error types to be returned

- 400: bad_request
- 404: not_found
- 405: method_not_allowed
- 422: unprocessable_entity
- 500: internal_server_error

## Testing

With Postgres running, run

```sh
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
```

Then run the test file

```sh
python test_flaskr.py
```

## Authors

[Blessing E Ebowe](https://www.linkedin.com/in/blessingebowe/)
