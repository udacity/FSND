# Trivia API

## Description

This API powers the basic gameplay of a Trivia game:

- Display a random unknown question for X rounds (also for certain question category)
- Evaluate User's guess with hidden answer

Additionally, the API allows users to add, update & delete questions ([CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)). 

**Why should you contribute?**

If you're passionate about Trivia, you have the chance to finally realize game features that the original board game won't support. Feel like adding a clock to each user's turn? Implement hints? Your imagination is the limit.

(Also: This API is developed by a programming beginner, so your experience will help educate the creator(s) :-)

## Code Style

Python: [PEP8](https://www.python.org/dev/peps/pep-0008/)

JS: [AirBnB JS Style Guide](https://github.com/airbnb/javascript)

# Getting Started

## Prerequisites

This app runs with Python3 in the backend and Postgres for the Database.

- Python
    1. Ensure to have Python installed

        **Linux & macOS**

        There is a very good chance your Linux and/or macOS distribution has Python installed already, but it probably won’t be the latest version, and it may be Python 2 instead of Python 3.

        To find out what version(s) you have, open a terminal window and try the following commands:

        - `python --version`
        - `python2 --version`
        - `python3 --version`

        One or more of these commands should respond with a version, as below:

        ```bash
        $ python3 --version
        Python 3.8.1
        ```

        If the version shown is Python 2.x.x or a version of Python 3 that is not the latest (3.8.1 as of this writing), then you will want to install the latest version.

        **Windows**

        Windows usually does not come with Python installed. You can still see if you had installed anything in the past using `python` command in the PowerShell or command prompt.

        If you have a Python version installed, PowerShell should respond with its version like below:

        ```powershell
        C:\Users\{user-name}>python
        Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 23:11:46) [MSC v.1916 64 bit (AMD64)] on win32
        Type "help", "copyright", "credits" or "license" for more information.
        >>>
        ```

    2. Install the latest version

        [This article](https://realpython.com/installing-python/) outlines a guide for all kinds of distributions on how to install Python.

- Postgres
    1. Ensure to have Postgres installed

        **Linux & macOS**

        To find the Postgres server version from the shell command line, simply issue a `postgres` command with the `-V` flag (for version):

        ```bash
        $ postgres -V
        postgres (PostgreSQL) 9.3.10
        ```

        In the event that the `postgres` command is not found, you may need to locate the directory of the utility. This can be done by issuing the `locate bin/postgres` command:

        ```bash
        $ locate bin/postgres
        /usr/lib/postgresql/9.3/bin/postgres
        ```

        Now with the direct path to the `postgres` utility, you can call it with the `-V` flag as illustrated above:

        ```bash
        $ /usr/lib/postgresql/9.3/bin/postgres -V
        postgres (PostgreSQL) 9.3.10
        ```

        **Windows**

        `postgres -V` works also in the PowerShell, however locating the postgres installation directory is different:

        ```powershell
        C:\Users\{user-name}>ls c:\ *postgres* -Recurse -Directory

            Directory: C:\Program Files

        Mode                LastWriteTime         Length Name
        ----                -------------         ------ ----
        d-----        2/16/2020   6:39 PM                PostgreSQL

            Directory: C:\Program Files\PostgreSQL\12\doc

        Mode                LastWriteTime         Length Name
        ----                -------------         ------ ----
        d-----        2/16/2020   6:39 PM                postgresql
        ```

    2. Install if not present

        Please refer to the [official documentation](https://www.postgresql.org/docs/9.3/tutorial-install.html)

- Node
    1. Ensure to have NPM/Yarn installed
        - **macOS & Linux**

            Check npm's version: `npm --version`
            ⇒ Upgrade:

            1. Latest version: `npm install -g npm@latest`
            2. Most recent release: `npm install -g npm@next`
        - **Windows**

            Check npm's version: `npm --version`
            ⇒ Upgrade: [Windows upgrade script](https://github.com/felixrieseberg/npm-windows-upgrade), or:

            1. `Set-ExecutionPolicy Unrestricted -Scope CurrentUser -Force`
            2. `npm install -g npm-windows-upgrade`
            3. `npm-windows-upgrade`
    2. Install if not present following [this article](https://nodejs.org/en/download/package-manager/)

## Set up local development environment

1. Clone the repo `git clone <project-url> <project-name>`
2. Create virtual Python environment
    - cd into `/<project-name>/backend`
    - Create environment `python -m venv <environment-name>`
    - Activate environment
        - macOS & Linux: `source <environment-name>/bin/activate`
        - Windows: `.\<environment-name>\Scripts\activate`
    - Install dependencies `pip install -r requirements.txt`
3. Create database
    - cd into `/<project-name>/backend`
    - Create database called 'trivia*'* `createdb trivia`
4. Migrate the database
    - cd into `/backend`
    - Export local environment variables (for Windows PowerShell run: `./export-flask-variables.ps1`)
    - Initialize the database `flask db init`
    - Upgrade database to latest migration `flask db upgrade`
5. Insert Data
    - Windows:
        1. Open `prepare-dev-db.ps1` in editor and insert passwort & user
        2. Run `prepare-dev-db.ps1`
    - macOS & Linux:
        1. `psql trivia < trivia.psql`
        2. `psql trivia < trivia.psql`
        3. `psql trivia < trivia.psql`

## Testing

The single testing module is stored in `/<project-name>/backend/test_flaskr.py`

It contains all tests for the backend of the API. 

Currently, the API does not support frontend tests.

Tests functions are defined in a way that they do not require *insertion*, *modification* or *deletion* after having ran the test. To run a test, make sure to restore the database beforehand as explained [above](https://www.notion.so/README-md-53126aec53f64ba386f3f4deb8eb7675#b011f67ac4ba44608578a9fba52e1194).

The API has implemented tests using [unittest](https://docs.python.org/2/library/unittest.html), so you can execute the tests as follows:

- Executing entire module

    In `/backend` directory run `python -m unittest test_flaskr`

    Alternatively, run `python /<project-name>/backend/test_flaskr.py`

    python -m unittest test_module.TestClass

- Executing single methods

    In `/backend` directory run `python -m unittest test_flaskr.BooksTestClass.<test_method>`

Lastly, all backend tests are kept in that file and should be maintained as updates are made to app functionality. Note that the naming convention for a test is:

`test_xxx_<test-name>`, where `xxx` is the test number. This enables chronological execution of tests.

# API Reference

## Quick start

- Base URL

    There is no base URL hosted as this API is not deployed yet. This means that the Base URL will only be available locally takes the Flask default, namely:

    - `http://localhost:5000`, or
    - `http://127.0.0.1:5000`

    Please note that the frontend is developed in React, which takes in Request on the 3000 port by default. In order to circumvent CORS issues (different ports are considered cross origin), we proxy every request unknown to the React app to the 5000 port in its `frontend/package.json` file.

- Authentication

    As of now, the API does not support authentication. It runs only locally.

## Error Handling

- Response layout

    The API sends a JSON-encoded response for errors containing information about success, error code and its name and description. The format takes [werkzeug's HTTP Exceptions](https://werkzeug.palletsprojects.com/en/1.0.x/exceptions/).

    For example, if the API could [not find](https://werkzeug.palletsprojects.com/en/1.0.x/exceptions/#werkzeug.exceptions.NotFound) the requested resource it may respond in the following manner:

    ```json
    {
    	"success": False,
    	"error_code": 404,
    	"error_name": "Not Found"
    	"desscription": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
    }
    ```

- Overview of error codes

    [Error Codes handled by API - Table](https://www.notion.so/ecbfc4fb7bee47e9879d415e853886ec)

    Error Codes handled by API - List:

    - **400 - Bad Request**

        The browser (or proxy) sent a request that this server could not understand.

    - **404 - Not Found**

        The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.

    - **422 - Unprocessable Entity**

        The request was well-formed but was unable to be followed due to semantic errors.

    - **500 - Internal Server Error**

        The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.

## API Endpoints

### `GET /api/questions`

- General
    - **Action:** Retrieves all questions
    - **Arguments & Data:** Takes `page` and `current_category` argument passed via *query parameter*
    - **Returns:** JSON-encoded response with paginated questions as well as a categories, the number of total questions and the category ('all' if not provided).
    - **Pagination:** Responses are paginated with 10 questions per page.
- Example Request

    ```bash
    curl --request GET localhost:5000/api/questions
    ```

- Sample Response

    ```json
    {"categories": {"1":Science,
    	"2":Art,
    	"3":Geography,
    	"4":History,
    	"5":Entertainment,
    	"6":Sports},
    "current_category": "all",
    "page": 1,
    "questions": {
    	{"answer": "Apollo 13",
    	"category_id": 5,
    	"difficulty": 4;,
    	"id": 2,
    	"question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    	}, {...},
    	{"answer": "Tom Cruise",
    	"category_id": 5,
    	"difficulty": 4,
    	"id": 4,
    	"question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    	}
    },
    "success": True,
    "total_categories": 7,
    "total_questions" : 20
    }
    ```

### `POST /api/questions`

- General
    - **Action:** Inserts question into database if:
        - body contains required params (see below)
        - No duplicate question is found
    - **Arguments & Data:** Takes a JSON encoded data request with the following arguments:
        - `question`*
        - `answer`*
        - `difficulty`*
        - `category`
    - **Returns:** JSON-encoded response with the created question as well as a categories, the number of total questions and the current category ('all' if not provided).
    - **Pagination:** No pagination.
- Example Request

    ```bash
    curl -d '{
                "question": {
                    "question": "How old are you?"
                    , "answer": "Too old"
                    , "difficulty": 5
                    },
                "current_category": 1
            }' 'http://127.0.0.1:5000/api/questions'
    ```

- Sample Response

    ```json
    {
        "created": {
            "answer": "Too old.",
            "category_id": 7,
            "difficulty": 5,
            "id": 35,
            "question": "How old am I?"
        },
        "current_category": "all",
        "page": 1,
        "questions": [{
                "answer": "Apollo 13",
                "category_id": 5,
                "difficulty": 4,
                "id": 2,
                "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
            },
            {
                "answer": "Tom Cruise",
                "category_id": 5,
                "difficulty": 4,
                "id": 4,
                "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
            },
            {
                "answer": "Maya Angelou",
                "category_id": 4,
                "difficulty": 2,
                "id": 5,
                "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
            },
            {
                "answer": "Edward Scissorhands",
                "category_id": 5,
                "difficulty": 3,
                "id": 6,
                "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
            },
            {
                "answer": "Brazil",
                "category_id": 6,
                "difficulty": 3,
                "id": 10,
                "question": "Which is the only team to play in every soccer World Cup tournament?"
            },
            {
                "answer": "Uruguay",
                "category_id": 6,
                "difficulty": 4,
                "id": 11,
                "question": "Which country won the first ever soccer World Cup in 1930?"
            },
            {
                "answer": "George Washington Carver",
                "category_id": 4,
                "difficulty": 2,
                "id": 12,
                "question": "Who invented Peanut Butter?"
            },
            {
                "answer": "Lake Victoria",
                "category_id": 3,
                "difficulty": 2,
                "id": 13,
                "question": "What is the largest lake in Africa?"
            },
            {
                "answer": "The Palace of Versailles",
                "category_id": 3,
                "difficulty": 3,
                "id": 14,
                "question": "In which royal palace would you find the Hall of Mirrors?"
            },
            {
                "answer": "Agra",
                "category_id": 3,
                "difficulty": 2,
                "id": 15,
                "question": "The Taj Mahal is located in which Indian city?"
            }
        ],
        "success": true,
        "total_categories": 7,
        "total_questions": 21
    }
    ```

### `GET /api/categories`

- General
    - **Action:** Retrieves all categories
    - **Arguments & Data:** Does not take any data
    - **Returns:** JSON-encoded response with categories, number of total categories and questions, page and current category ('all' if not provided).
    - **Pagination:** No pagination.
- Example Request

    ```bash
    curl 'http://127.0.0.1:5000/api/categories'
    ```

- Sample Response

    ```json
    {
        "categories": {
            "1": "Science",
            "2": "Art",
            "3": "Geography",
            "4": "History",
            "5": "Entertainment",
            "6": "Sports",
            "7": "Without Category"
        },
        "current_category": "all",
        "page": 1,
        "success": true,
        "total_categories": 7,
        "total_questions": 22
    }
    ```

### `GET /api/questions/categories/<category_id>`

- General
    - **Action:** Retrieves all questions for a given category
    - **Arguments & Data:** `category_id` must be stated in endpoint, no further data supported.
    - **Returns:** JSON-encoded response with paginated questions, number of total categories and questions, page and current category.
    - **Pagination:** Responses are paginated with 10 questions per page.
- Example Request

    ```bash
    curl http://127.0.0.1:5000/api/questions/categories/2
    ```

- Sample Response

    ```json
    {
        "current_category": 2,
        "page": 1,
        "questions": [{
                "answer": "Escher",
                "category_id": 2,
                "difficulty": 1,
                "id": 16,
                "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
            },
            {
                "answer": "Mona Lisa",
                "category_id": 2,
                "difficulty": 3,
                "id": 17,
                "question": "La Giaconda is better known as what?"
            },
            {
                "answer": "One",
                "category_id": 2,
                "difficulty": 4,
                "id": 18,
                "question": "How many paintings did Van Gogh sell in his lifetime?"
            },
            {
                "answer": "Jackson Pollock",
                "category_id": 2,
                "difficulty": 2,
                "id": 19,
                "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
            }
        ],
        "success": true,
        "total_categories": 7,
        "total_questions": 4
    }
    ```

### `DELETE /api/questions/<question_id>`

- General
    - **Action:** Deletes the question from the database.
    - **Arguments & Data:** The `question_id` must be specified as an `integer` in the endpoint.
    - **Returns:** JSON-encoded response with the deleted question, number of total categories and questions, page and current category ('all' if not provided).
    - **Pagination:** No pagination for the single question.
- Example Request

    ```bash
    curl --verbose  --request "DELETE" "http://127.0.0.1:5000/api/questions/36"
    ```

- Sample Response

    ```json
    {
        "current_category": "all",
        "deleted": {
            "answer": "Too old",
            "category_id": 7,
            "difficulty": 5,
            "id": 36,
            "question": "How old are you?"
        },
        "page": 1,
        "success": true,
        "total_categories": 7,
        "total_questions": 21
    }
    ```

### `POST /api/questions/searches`

- General
    - **Action:** Searches for questions in the database
    - **Arguments & Data:** Takes data (`page`*, `searchTerm`*, `searchOnAnswer`) passed via JSON.
    - **Returns:** JSON-encoded response with questions returned by query as well as search term, number of categories found, number of questions found and page.
    - **Pagination:** Responses are paginated with 10 questions per page.
- Example Request

    ```bash
    curl --verbose --data '{"searchTerm": "a"}' --request "POST" "http://127.0.0.1:5000/api/questions/searches"
    ```

- Sample Response

    ```json
    {
        "page": 1,
        "questions": [{
                "answer": "Maya Angelou",
                "category_id": 4,
                "difficulty": 2,
                "id": 5,
                "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
            },
            {
                "answer": "Apollo 13",
                "category_id": 5,
                "difficulty": 4,
                "id": 2,
                "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
            },
            {
                "answer": "Tom Cruise",
                "category_id": 5,
                "difficulty": 4,
                "id": 4,
                "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
            },
            {
                "answer": "Edward Scissorhands",
                "category_id": 5,
                "difficulty": 3,
                "id": 6,
                "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
            },
            {
                "answer": "Brazil",
                "category_id": 6,
                "difficulty": 3,
                "id": 10,
                "question": "Which is the only team to play in every soccer World Cup tournament?"
            },
            {
                "answer": "George Washington Carver",
                "category_id": 4,
                "difficulty": 2,
                "id": 12,
                "question": "Who invented Peanut Butter?"
            },
            {
                "answer": "Lake Victoria",
                "category_id": 3,
                "difficulty": 2,
                "id": 13,
                "question": "What is the largest lake in Africa?"
            },
            {
                "answer": "The Palace of Versailles",
                "category_id": 3,
                "difficulty": 3,
                "id": 14,
                "question": "In which royal palace would you find the Hall of Mirrors?"
            },
            {
                "answer": "Agra",
                "category_id": 3,
                "difficulty": 2,
                "id": 15,
                "question": "The Taj Mahal is located in which Indian city?"
            },
            {
                "answer": "Escher",
                "category_id": 2,
                "difficulty": 1,
                "id": 16,
                "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
            }
        ],
        "search_term": "a",
        "success": true,
        "total_categories": 7,
        "total_questions": 16
    }
    ```

### `POST /api/categories/searches`

- General
    - **Action:** Searches for categories in the database
    - **Arguments & Data:** Takes data (`page`* and `searchTerm`*) passed via JSON.
    - **Returns:** JSON-encoded response with categories returned by query as well as search term, number of categories found and page.
    - **Pagination:** No pagination.
- Example Request

    ```bash
    curl --verbose --data '{"searchTerm": "a"}' --request "POST" "http://127.0.0.1:5000/api/categories/searches"
    ```

- Sample Response

    ```json
    {
        "categories": [{
                "id": 2,
                "type": "Art"
            },
            {
                "id": 3,
                "type": "Geography"
            },
            {
                "id": 5,
                "type": "Entertainment"
            },
            {
                "id": 7,
                "type": "Without Category"
            }
        ],
        "page": 1,
        "search_term": "a",
        "success": true,
        "total_categories": 4
    }
    ```

# Deployment

This API is not deployed yet.

# Authors

[Richard Poelderl](https://github.com/p6l-richard/)

# Acknowledgments

Inspiration from [Caryn McCarthy](http://github.com/cmccarthy15) of Udacity.