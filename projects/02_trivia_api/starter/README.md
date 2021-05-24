# Full Stack Trivia

## Trivia API Overview

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a  webpage to manage the trivia app and play the game. 

The Trivia webpage has a few key features that make this a fun experience for everyone. The features are not just limited to the webpage, but anyone who wants
to interact with our API. The following features are publicly available to users of our trivia API:
1) Get Questions - both all questions and by category. 
2) Delete questions.
3) Add questions and require that they include question and answer text.
4) Search for questions based on a text query string.
5) Simulate a quiz game by requesting questions by a specific category and keeping track of previous questiosn. 

## Getting started with our API

Base URL: When you run our backend app, you can make use of the URL that is hosted at the default, http://127.0.0.1:5000/, which is set as a proxy in the frontend configuration.

Authentication: This version of the application does not require authentication or API keys.

## Error Handling
Errors in our API are returned as JSON objects. Here's an example of an error from a 'Bad request':
```
{
    "success": False, 
    "error": 400,
    "message": "Bad request"
}
```

The API will return three error types when requests fail:

- 400: Bad Request
- 404: Resource Not Found
- 405: Not Allowed 
- 422: Not Processable/Unprocessable
    
## Endpoints
### GET /questions
#### General:
- Returns a list of all questions, success value, and total number of questions
- Results are paginated in groups of 10. Include a request argument (e.g. page=2) to choose page number, default from 1. 
- Sample: `curl http://127.0.0.1:5000/questions?page=2`

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
  "current_category": "Geography", 
  "questions": [
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "One", 
      "category": 2, 
      "difficulty": 4, 
      "id": 18, 
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    }, 
    {
      "answer": "Jackson Pollock", 
      "category": 2, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }, 
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
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "Scarab", 
      "category": 4, 
      "difficulty": 4, 
      "id": 23, 
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }, 
    {
      "answer": "Shakespere", 
      "category": 2, 
      "difficulty": 1, 
      "id": 24, 
      "question": "Who wrote Hamlet?"
    }
  ], 
  "success": true, 
  "total_questions": 18
}
```

### GET /categories
#### General:
- Returns a list of all categories of questions.
- Returns a success code
- Results include the type and id of the category - this is useful if you want to add a dropdown menu where the value matches a category id. 
- Sample: `curl http://127.0.0.1:5000/categories

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
  "success": true
}
```