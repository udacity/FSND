# Backend - Full Stack Trivia API
### Description
This project  in the  cource “API Development and Documentation” of the Full Stack Web Developer Nanodegree Program. I implemented and  completed the necessary tasks and learned a lot. By completing this project, I learn implementing well formatted API endpoints, writing documentation and etc. Thanks Udacity’s team!

### Pre-requisites
### Installing Dependencies
Developers using this project should already have postgresql, Python3, pip and node installed on their local machines.

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```
### Running Server
### Backend

To run the application run the following commands:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

The application is run on http://127.0.0.1:5000/ by default and is a proxy in the frontend configuration.

### Frontend

From the frontend folder, run the following commands to start the client:

```bash
npm install // only once to install dependencies
npm start
```
By default, the frontend will run on localhost:3000.

### Testing

Before running test create  database trivia_test in the PostgreSQL server.

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
```

To run the flask tests, from the backend folder in terminal run the following command:

```bash
python test_flaskr.py
```
### API Documentation
### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the     default, http://127.0.0.1:5000/, which is set as a proxy in the frontend configuration.
- Authentication: This version of the application does not require authentication or API keys

### Errors
Errors are returned as JSON objects in the following format:

```bash
{
    "success": False,
    "error": 405,
    "message": "Method Not Allowed."
}
```
The API will return following error types when requests fail:
- 400: Bad Request.
- 404: The requested resource doesn't exist.
- 405: Method Not Allowed.
- 422: Unprocessable Entity.
- 500: Internal Server Error.

### Endpoints
#### GET /categories
- General: Returns a list of categories
- Sample `curl http://127.0.0.1:5000/categories`

```bash
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
#### GET /questions
- General:
    - Returns a list of questions, number of total questions, current category, categories.
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
- Sample: `curl http://127.0.0.1:5000/questions?page=2`

```bash
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
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
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
    },
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
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
    },
    {
      "answer": "Lake Victoria",
      "category": 3,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": 3,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }
  ],
  "success": true,
  "total_questions": 20
}
```

#### DELETE /question/<int:id>
- General
    - Deletes the question of the given ID if it exists
    - Returns the id of the deleted question
- Sample: `curl http://127.0.0.1:5000/questions/4 -X DELETE`
```bash
{
  "success":True,
  "id":4,
}
```
#### POST /questions  to create new question
- General
    - Creates new question.
    - Returns id of the created question and success value
- Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{ "question": "The consept of gravity was discovered by which famous phisicist?", "answer": "Sir Isaac Newton", "difficulty": 3, "category": "1" }'`

```bash
{
  "created": 25,
  "success": true
}
```
#### POST /questions  to search question
- General
    - Searches questions based on search term
    - Returns any questions for whom the search term is a substring of the question.
    - Also returns success value, total number of questions
    - Results are paginated in groups of 10.
- Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"searchTerm":"What"}'`

```bash
 "questions": [
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
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
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    },
    {
      "answer": "Lake Victoria",
      "category": 3,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "Mona Lisa",
      "category": 2,
      "difficulty": 3,
      "id": 17,
      "question": "La Giaconda is better known as what?"
    },
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Blood",
      "category": 1,
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ],
  "success": true,
  "total_questions": 8
}
```

#### GET /categories/<category_id>/questions
- General
    -Gets questions based on category
    -Return a list of questions, number of total questions, current category, categories.
- Sample: `curl http://127.0.0.1:5000/categories/3/questions`

```bash
{
  "currentCategory": "Geography",
  "questions": [
    {
      "answer": "Lake Victoria",
      "category": 3,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": 3,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    },
    {
      "answer": "Agra",
      "category": 3,
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

#### Post/quizzes
- General
    - Allows users to play the quiz game.
    - Get questions to play the quiz
    - Returns the random question which is not in previous questions, with the given category and success value
- Sample: `curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions": [], "quiz_category": {"type": "History", "id": "4"}}'`

```bash
{
  "question": {
    "answer": "Muhammad Ali",
    "category": 4,
    "difficulty": 1,
    "id": 9,
    "question": "What boxer's original name is Cassius Clay?"
  },
  "success": true
}
```

### Authors
This project was created by  Udacity as a project template for the Full Stack Web Developer Nanodegree.
Shahzod Ashumatov implemented ToDo Tasks in (__init__.py) and (test_flaskr.py), wrote this README