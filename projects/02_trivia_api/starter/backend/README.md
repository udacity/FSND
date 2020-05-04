# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

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

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

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

## Endpoints

### GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category.
- Request Arguments: None
- Returns: An object with a single key, categories, that contains an object of id: category_string key:value pairs. Also includes the total categories quantity.
```
{
  "categories":{
    "1" : "Science",
    "2" : "Art",
    "3" : "Geography",
    "4" : "History",
    "5" : "Entertainment",
    "6" : "Sports"
   },
   "total_categories": 6
```

### GET '/questions'
- Fetches a dictionary of questions in which the keys are the fields of the Question model and the values are the corresponding string of the fields.
- Request Arguments: None
- Returns: An object with keys, Question model fields, and the total of questions. Also includes the categories.
```
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null,
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    ...
  ],
  "success": true,
  "total_questions": 19
}
```

### DELETE '/questions/<int:question_id>'
- Deletes a specific questions.
- Request Arguments: Question ID.
- Returns: The deleted question ID, the remaining questions, and the quantity of them.
```
{
  "questions": [...],
  "deleted": <question_id>,
  "success": true,
  "total_questions": 18
}
```

### POST '/questions' to create a new question
- Creates a new question.
- Request Arguments: A JSON object with the key:values of the Question model fields.
```
{
  "question": "Test question",
  "answer": "Test",
  "category": 5,
  "difficulty": 1
}
```
- Returns the created question ID, the new list of questions, and the new total quantity of them.
```
{
  "questions": [...],
  "created": <question_id>,
  "success": true,
  "total_questions": 19
}
```

### POST '/questions' to search for questions
- Search for questions.
- Request Arguments: A JSON object with the key:value of the search term.
```
{
  "searchTerm": 'Test search'
}
```
- Returns the questions of the search executed and the total quantity of them.
```
{
  "questions": [...],
  "success": true,
  "total_questions": 19
}
```

### GET '/categories/<int:category_id>/questions'
- Fetches for questions from a specific category.
- Request Arguments: Category ID.
- Returns: The category ID, the questions of that category, and the quantity of them.
```
{
  "questions": [...],
  "current_category": <category_id>,
  "success": true,
  "total_questions": 18
}
```

### POST '/quizzes'
- Fetches for new questions to continue the game. When there is not more questions, the returned question will be None.
- Request Arguments: A JSON object with the key:value of the Category model fields and an array of the previous questions IDs.
```
{
  "previous_questions": [1, 2, ...],
  "quiz_category": {
    "id": "5",
    "type": "Entertaiment"
  }
}
```
- Returns the next question randomly.
```
{
  "question": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }
  ],
  "success": true
}
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```