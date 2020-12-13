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

REVIEW_COMMENT
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints
GET '/categories'
GET '/categories/<int:category_id>'
GET '/questions'
DELETE '/questions/<int:question_id>'
POST '/questions/add'
POST '/questions/search'
POST '/quizzes'


GET '/categories'
- Fetches a list of category names
- Request Arguments: None
- Returns: A list of categories in String type, as shown below:
    {
        "categories":["Science","Art","Geography","History","Entertainment","Sports"],"success":true
    }


GET '/categories/<int:category_id>'
- Fetches all questions that belong to a specific category set by category_id
- Request Arguments: category_id which is supposed to be an integer
- Returns: A list of question objects and each question has 5 keys ('answer','category','difficulty','id', and 'question') as well as their corresponding values, as shown below:
    {
        "current_category":[2,"Art"],
        "questions":[
            {
                "answer":"Escher",
                "category":2,
                "difficulty":1,
                "id":16,
                "question":"Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
            },
            {
                "answer":"Jackson Pollock",
                "category":2,
                "difficulty":2,
                "id":19,
                "question":"Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
            }
            ],
            "success":true,
            "total_questions":2
    }


GET '/questions'
- Fetches all questions
- Request Arguments: None
- Returns: all questions, all categories and number of questions, as shown below:
{
    "categories":["Science","Art","Geography","History","Entertainment","Sports"],"current_Category":"Science",
    "questions":[
        {
            "answer":"Apollo 13","category":5,"difficulty":4,
            "id":2,
            "question":"What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer":"Tom Cruise",
            "category":5,
            "difficulty":4,
            "id":4,
            "question":"What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        },
        {
            "answer":"Maya Angelou",
            "category":4,
            "difficulty":2,
            "id":5,
            "question":"Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
        }
    ],
    "success":true,
    "total_questions":3
}


DELETE '/questions/<int:question_id>'
- Delete a specific question based on question_id
- Request Arguments: question_id
- Returns: success, as shown below:
    {"success":true}


POST '/questions/add'
- Add a new question
- Request Arguments: new question information including answer,category, difficulty level and question text, as shown below:
    {'answer': '1', 'category': 1, 'difficulty': 1, 'question': 'new question 1'}
- Returns: success, as shown below:
    {"success":true}


POST '/questions/search'
- get questions based on a search term. 
- Request Arguments: searchTerm in the format as shown below:
    {'searchTerm': 'actor'}
- Returns: It returns any questions for whom the search term is a substring of the question. One example is shown below:
{
  questions: [
    {
      answer: "Tom Cruise",
      category: 5,
      difficulty: 4,
      id: 4,
      question: "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?",
    }
  ],
  success: true,
  "total questions": 1,
}


POST '/quizzes'
- Fetches quizzes for all categories or based on a specific category 
- Request Arguments: previous_questions, quiz_category which includes 'id' and 'type'. 'type' can be 'click' (all categories) or any one specific category name). 'id' is not used in the current function implementation and can be set to '0'. Two examples are shown below:
{
    'previous_questions': [], 
    'quiz_category': {'id': 0, 'type': 'click'}
}

{
    'previous_questions': [18, 19],
    'quiz_category': {'id': '1', 'type': 'Art'}
}

- Returns: next question to display, as shown below:
{
  question: {
    answer: "Muhammad Ali",
    category: 4,
    difficulty: 1,
    id: 9,
    question: "What boxer's original name is Cassius Clay?",
  },
  success: true
}



## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```