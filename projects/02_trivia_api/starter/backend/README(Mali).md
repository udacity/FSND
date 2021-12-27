# Backend - Full Stack Trivia API 

This project is a virtual quizz app for Udacity students to demonstrate their API skills. Students are able to add their questions and their answers based on pre-defined categories. The application allow querying and searching questions as well as adding new questions. It is also possible to play a quizz. Application returns a new question each time the current question is answered. Application is able to hold a list of answered questions and not returning the same question 

### Installing Dependencies for the Backend
Developers using this project should already have Python3, pip and node installed on their local machines.

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Environment** - It is recommended working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by navigating to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, use triviadbcreate.sql file to create both "trivia" and "trivia_test" dbs along with test user "mali". After that From the backend folder in terminal run:

```bash
psql triviadbcreate.
psql trivia < trivia.psql
```

### Running the backend server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the application run the following commands within the "backend" folder: 
```
export FLASK_APP=flaskr
export FLASK_ENV=development

flask run
```

These commands put the application in development and directs our application to use the `__init__.py` file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the [Flask documentation](http://flask.pocoo.org/docs/1.0/tutorial/factory/).

The application is run on `http://127.0.0.1:5000/` by default and is a proxy in the frontend configuration. 

#### Frontend

From the frontend folder, run the following commands to start the client: 
```
npm install // only once to install dependencies
npm start 
```

By default, the frontend will run on localhost:3000. 

### Tests
In order to run tests navigate to the backend folder and run the following commands: 

```
python test_flaskr.py
```

Before running the tests make sure the "trivia_test" database is already created as it is described in "running the backend server" section. 

All tests are kept in that file and should be maintained as updates are made to app functionality. 

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 404,
    "message": "Resource Not Found"
}
```
The API will return following error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 405: Method Not Allowed 
- 422: Not Processable 
- 500: Internal Server Error 

### Endpoints 
#### GET
##### /questions
- General:
    - Returns a list of questions, categories, success value, and total number of questions
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1. 
- Sample: `curl http://127.0.0.1:5000/questions?page=1`
'''
{
    "categories": {
        "0": "All",
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "currentCategory": "All",
    "questions": [
        {
            "answer": "Muhammad Ali",
            "category": 4,
            "difficulty": 1,
            "id": 1,
            "question": "What boxer's original name is Cassius Clay?"
        },
        {
            "answer": "Maya Angelou",
            "category": 4,
            "difficulty": 2,
            "id": 2,
            "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings?'"
        },
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 3,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Tom Cruise",
            "category": 5,
            "difficulty": 4,
            "id": 4,
            "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        },
        {
            "answer": "Edward Scissorhands",
            "category": 5,
            "difficulty": 3,
            "id": 5,
            "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        },
        {
            "answer": "Brazil",
            "category": 6,
            "difficulty": 3,
            "id": 6,
            "question": "Which is the only team to play in every soccer World Cup tournament?"
        },
        {
            "answer": "Uruguay",
            "category": 6,
            "difficulty": 4,
            "id": 7,
            "question": "Which country won the first ever soccer World Cup in 1930?"
        },
        {
            "answer": "George Washington Carver",
            "category": 4,
            "difficulty": 2,
            "id": 8,
            "question": "Who invented Peanut Butter?"
        },
        {
            "answer": "Lake Victoria",
            "category": 3,
            "difficulty": 2,
            "id": 9,
            "question": "What is the largest lake in Africa?"
        },
        {
            "answer": "The Palace of Versailles",
            "category": 3,
            "difficulty": 3,
            "id": 10,
            "question": "In which royal palace would you find the Hall of Mirrors?"
        }
    ],
    "success": true,
    "totalQuestions": 21
}
'''

##### /questions/<question_id>
- General:
    - Returns a specific question, total number of questions and success value
- Sample: `curl http://127.0.0.1:5000/questions/1`
'''
{
    "question": {
        "answer": "Muhammad Ali",
        "category": 4,
        "difficulty": 1,
        "id": 1,
        "question": "What boxer's original name is Cassius Clay?"
    },
    "success": true,
    "totalQuestions": 21
}
'''

##### /categories
- General:
    - Returns a list of categories and success value
- Sample: `curl http://127.0.0.1:5000/categories`
'''
{
    "categories": {
        "0": "All",
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "success": true
}
'''
##### /categories/<category_id>/questions
- General:
    - Returns a list of questions which belongs to the given category
- Sample: `curl http://127.0.0.1:5000/categories/1/questions`
'''
{
    "currentCategory": "Science",
    "questions": [
        {
            "answer": "The Liver",
            "category": 1,
            "difficulty": 4,
            "id": 16,
            "question": "What is the heaviest organ in the human body?"
        },
        {
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3,
            "id": 17,
            "question": "Who discovered penicillin?"
        },
        {
            "answer": "Blood",
            "category": 1,
            "difficulty": 4,
            "id": 18,
            "question": "Hematology is a branch of medicine involving the study of what?"
        }
    ],
    "success": true
}
'''
#### DELETE
##### /questions/<question_id>
- General:
    - Deletes the question of given id if it exsists. Returns success value and total number of questions
- Sample: `curl -X DELETE http://127.0.0.1:5000/questions/26`
'''
{
    "success": true,
    "totalQuestions": 20
}
'''
#### POST
##### /questions
- General:
    - Creates a new question using the submitted questions, answer, difficulty and category. Returns the the created question and success value. 
- `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '               {"question":"Capital City of France?", "answer": "Paris", "difficulty": "1", "category":"5"}'`
'''
{
    "question": {
        "answer": "Paris",
        "category": 5,
        "difficulty": 1,
        "id": 27,
        "question": "Capital City of France?"
    },
    "success": true
}
'''
##### /questions/search
- General:
    - Searches and returns all the questions which contains the search term. Also returns success code and total number of questions. 
- `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '               {"searchTerm":"world"}'`
'''
{
    "questions": [
        {
            "answer": "Brazil",
            "category": 6,
            "difficulty": 3,
            "id": 6,
            "question": "Which is the only team to play in every soccer World Cup tournament?"
        },
        {
            "answer": "Uruguay",
            "category": 6,
            "difficulty": 4,
            "id": 7,
            "question": "Which country won the first ever soccer World Cup in 1930?"
        }
    ],
    "success": true,
    "totalQuestions": 21
}
'''
##### /quizzes
- General:
    - This endpoint takes category and previous question parameters and return a random question within the given category.  
- `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '               {"previous_questions": ["17","18"],"quiz_category": {"type": "Science","id": "1"}}'`
'''
{
    "question": {
        "answer": "The Liver",
        "category": 1,
        "difficulty": 4,
        "id": 16,
        "question": "What is the heaviest organ in the human body?"
    },
    "success": true
}
'''
## Deployment N/A

## Authors
Mehmet Ali OK & Udacity Team 

## Acknowledgements 
The awesome team at Udacity! 