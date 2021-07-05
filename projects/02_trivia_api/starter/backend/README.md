# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## ToDo Tasks
These are the files you'd want to edit in the backend:

1. *./backend/flaskr/`__init__.py`*
2. *./backend/test_flaskr.py*


One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 


2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 


3. Create an endpoint to handle GET requests for all available categories. 


4. Create an endpoint to DELETE question using a question ID. 


5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 


6. Create a POST endpoint to get questions based on category. 


7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 


8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 


9. Create error handlers for all expected errors including 400, 404, 422 and 500. 



## Review Comment to the Students
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints
GET '/api/v1.0/categories'
GET ...
POST ...
DELETE ...

GET '/api/v1.0/categories'
- Fetches an array of categories in which the keys are `id` and `type`. `type` is the category name.
- Request Parameter: None
- Returns: JSON object with "categories" property. 
{
  "categories": [
    {
      "id": <int>,
      "type": <string>
    },
    {
      "id": 2,
      "type": "Art"
    },
    {
      "id": 5,
      "type": "Entertainment"
    },
    {
      "id": 3,
      "type": "Geography"
    },
    {
      "id": 4,
      "type": "History"
    },
    {
      "id": 1,
      "type": "Science"
    },
    {
      "id": 6,
      "type": "Sports"
    }
  ]
}


GET '/api/v1.0/questions'
- Fetches an oject in which the keys are `questions`, `total_questions`, `categories`, and `current_category`. Pagination is supported with `page` query parameter. Maximum of 10 `questions` are returned.
- Request query parameter: page number in integer format.
- Returns: JSON object with "questions", "total_questions", "categories", and "current_category" properties. 
{
    "questions": [
        {
            'id': <int>,
            'question': <string>,
            'answer': <string>,
            'category': <int>,
            'difficulty': <int>
        }
    ],
    "total_questions": <int>, 
    "categories": [
        { `see GET '/api/v1.0/categories' endpoint`}
    ],
    "current_category": <string>
}


DELETE '/api/v1.0/questions/<int:question_id>'
- Deletes a question. If question was not found, returns 404
- Request parameter: question id to delete in integer format.
- Returns: JSON object with "success", and "message" with deleted question id.
{
    "success": <bool>,
    "message": <string>
}
{
    "success": True,
    "message": "Deleted 5"
}

POST '/api/v1.0/questions'
- Create a question. If required parameters were not satisfied, returns 400
- Request parameters: 
{
    "question": <string, required>,
    "answer": <string, required>,
    "category": <int, required>,
    "difficulty": <int, required>
}
- Returns: JSON object with "success", and "qid" properties. "qid" is the id for the newly created question.
{
    "success": <bool>,
    "qid": <int>
}

POST '/api/v1.0/search/questions'
- Search for questions based on search parameter.
- Request parameter:
{
    "searchTerm": <string> eg. title
}
- Returns: JSON object with "questions", "total_questions", "categories", and "current_category" properties. 
{
    "questions": [
        {
            'id': <int>,
            'question': <string>,
            'answer': <string>,
            'category': <int>,
            'difficulty': <int>
        }
    ],
    "total_questions": <int>, 
    "categories": [
        { `see GET '/api/v1.0/categories' endpoint`}
    ],
    "current_category": <string>
}

GET '/api/v1.0/categories/<int:category_id>/questions'
- Get questions within a category. 
- Request parameter: category_id <int>, required
- Returns: JSON object with "questions", "total_questions", "categories", and "current_category" properties. 
{
    "questions": [
        {
            'id': <int>,
            'question': <string>,
            'answer': <string>,
            'category': <int>,
            'difficulty': <int>
        }
    ],
    "total_questions": <int>, 
    "categories": [
        { `see GET '/api/v1.0/categories' endpoint`}
    ],
    "current_category": <string>
}


POST '/api/v1.0/quizzes'
- This endpoint takes category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
- Request parameter:
{
    "quiz_category": {
        "id": <int>
    },
    "previous_questions: [<int>] ie. previous answered question ids
}
- Returns: JSON object with "questions", "total_questions", "categories", and "current_category" properties. 
{
    "questions": [
        {
            'id': <int>,
            'question': <string>,
            'answer': <string>,
            'category': <int>,
            'difficulty': <int>
        }
    ],
    "total_questions": <int>, 
    "categories": [
        { `see GET '/api/v1.0/categories' endpoint`}
    ],
    "current_category": <string>
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
