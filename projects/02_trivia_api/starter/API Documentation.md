## Trivia API
The Trivia API provideds an interface for working with trivia question data.
Trivia questions include a question, answer, difficulty, and category.
The API supports creating, viewing, searching, and deleting trivia questions.
Additionally, trivia questions can be retrieved in a random order to provide a
trivia quizz from all or specific question categories.

### Getting Started
- Base URL: At the moment, the application can only be run locally and does
  not have a hosted base URL. The backend runs on the default, 
  `http://localhost:5000`.
- Authentication: Currently, the application does not require authentication
  or API keys.

### Error Handling
Errors are returnd as JSON objects in the following format:
```
{
    "message": "The browser (or proxy) sent a request that this server could not understand."
    "success": false,
    "type": "invalid_request_error",
}
```

Errors resulting from validatin errors contain an additional validation_errors key
with an array of objects in the following format:
```
{
    "message": "The request could not be processed because of invalid data.",
    "success": false,
    "type": "invalid_request_error",
    "validation_errors": [
        {
            "attribute": "quiz_category.id",
            "message": "A resource for the attribute \"quiz_category.id\" with the value \"20\" was not found.",
            "type": "not_found"
        }
    ]
}
``` 
Each validation error specifies the attribute, provides a message describing the error,
and belongs to a type of validation error. The validation errors can have the following
error types:
- attribute_required
- invalid_type
- number_out_of_range
- not_found

The API can respond to requests with the following HTTP status codes:
- 400: Bad Request
- 404: Not Found
- 405: Method Not Allowed
- 422: Not Processable
- 500 Internal Server Error

### Endpoints
Upon a succesful request, the JSON body will contain a `success` key
with a boolean value of `true`. Any request with an error will hold a value of `false`
in the `success` key.



#### GET /categories
- Fetches categories in the form of key value pairs where the key is the
  category id and the value is the category name
- Request Arguments: 
    - None
- Example:
    - Request path
        - `http://localhost:5000/categories`
    - Response body
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
    
#### GET /questions
- Fetches a list of questions paginated into groups of 10 under a `questions` key. 
  Each question includes a question id, question, answer, difficulty, and category id. 
  A dictionary of `category_id: category_string` is included under a `categories` key.
  Additionally, the total number of questions and current category id are also provided.
- Query Parameters:
    - page (optional)
        - a number representing the desired group of 10 questions
        - defaults to `1`
- Example:
    - Request path
        - `http://localhost:5000/questions`
    - Response body
        ```
        {
            "categories": {
                "1": "science",
                "2": "art",
                "3": "geography",
                "4": "history",
                "5": "entertainment",
                "6": "sports"
            },
            "current_category": null,
            "questions": [
                {
                    "answer": "Edward Scissorhands",
                    "category": 5,
                    "difficulty": 3,
                    "id": 6,
                    "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
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
                }
            ],
            "success": true,
            "total_questions": 3
        }
        ```

#### DELETE /questions/{question_id}
- Removes a question with the provided id
- Path Parameters:
    - question_id
- Example
    - Request path
        - `http://localhost:5000/questions/6`
    - Response body
        ```
        {
            "success": true
        }
        ```

#### POST /questions
- Serves the dual purpose of either creating a new question resource
  or returning questions matching a search term. The request is interpreted as a search when the `searchTerm` key is provided;
  otherwise, the request content is validated and used to create 
  a new question resource. During a search, the results will be 
  returned in the same format as the `GET /questions` endpoint, but the
  questions are not paginated. The search term matches text in any part
  of the question text and is case-insensitive. A question, answer, difficulty, and category id are required when creating a new
  question resource. Other validation includes: the difficulty must
  be an integer from 1 to 5 and the category must be an integer id for
  an existing category.
- Request Body Parameters
    - searchTerm
        - text to filter questions with matching text
        - required when searching questions
    - question
        - the question text
    - answer
        - the answer text
    - difficulty
        - how difficult the question is expected to be
        - 1 means the least difficult and
          5 means the most difficult
    - category
        - a category id
- Examples:
    - Search Questions
        - Request body
            ```
            {
                "searchTerm": "who"
            }
            ```
        - Response body
            ```
            {
                "current_category": null,
                "questions": [
                    {
                        "answer": "Alexander Fleming",
                        "category": 1,
                        "difficulty": 3,
                        "id": 21,
                        "question": "Who discovered penicillin?"
                    }
                ],
                "success": true,
                "total_questions": 1
            }
            ``` 
    - Create Question
        - Request body
            ```
            {
                "question": "What class of animal is a dog?",
                "answer": "Mammal",
                "category": 1,
                "difficulty": 1
            }
            ```
        - Response body
            ```
            {
                "success": true
            }
            ```

#### GET /categories/{category_id}/questions
- Fetches all questions having the category id provided. The response
  is formed in the same way as the `GET /questions` route, except
  questions are not paginated for this route.
- Path parameters
    - category_id
        - an id corresponding to an existing category resource
- Example
    - Request path
        - `http://localhost:5000/categories/1/questions`
    - Response body
        ```
        {
            "current_category": 1,
            "questions": [
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
                }
            ],
            "total_questions": 2
        }
        ```


#### POST /quizzes
- Fetches a random question from a specified category that is 
  not in the provided list of previous questions. The `quiz_category`
  should be an existing category id, but providing a value of `0` 
  will provide a question from any of the question categories.
- Request Body Parameters
    - quiz_category
        - an object containing an id key corresponding to an category
          resource
    - quiz_category.id
        - a category id
    - previous_questions
        - a list of question ids
        - represents the questions that have already been received and
          should not be the question that is returned
- Example
    - Request body
        ```
        {
            "quiz_category": {
                "id": 0
            },
            "previous_questions": []
        }
        ```
    - Response body
        ```
        {
            "question": {
                "answer": "Lake Victoria",
                "category": 3,
                "difficulty": 2,
                "id": 13,
                "question": "What is the largest lake in Africa?"
            },
            "success": 200
        }
        ```