import os
from flask import Flask, request, abort, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flasgger import Swagger

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # create swagger docs
    swagger = Swagger(app)

    # db init
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")

        return response

    """
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    """

    @app.route("/api/categories")
    def get_categories():
        """ 
        endpoint for retrieving all question categories
        ---
        responses:
            200:
                description: list of all categories
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Category'
                    example: [{"id":1,"type":"Science"},{"id":2,"type":"Art"}]
        """

        # get all categories
        categories = query_all_categories()

        res = {"categories": categories}

        return jsonify(res)

    def query_all_categories():
        """Query to get all categories. 

        Returns:
            List of all categories

        """

        categories = Category.query.all()
        formatted_categories = {cat.id: cat.type for cat in categories}
        return formatted_categories

    """
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    """

    @app.route("/api/questions")
    def get_questions():
        """ 
        returns all questions
        ---
        definitions:
            Category:
                type: object
                properties:
                    id: 
                        type: integer
                        example: 1
                    type:
                        type: string
                        example: Art
            Question:
                type: object
                properties:
                    id: 
                        type: integer
                        example: 2
                    question:
                        type: string
                        example: "What boxer's original name is Cassius Clay?"
                    answer:
                        type: string
                        example: Muhammad Ali
                    difficulty:
                        type: integer
                        example: 3
                    category:
                        type: integer
                        example: 2
        parameters:
          - name: q
            in: query
            type: string
            required: false
            description: query for question search
          - name: page
            in: query
            type: integer
            required: false
            description: cursor for paginated response
            default: 1
        response:
            200:
                description: list of all questions
                schema:
                    type: object
                    properties:
                        categories:
                            type: array
                            items:
                                $ref: '#/definitions/Category'
                            example: [{"id":1,"type":"Science"},{"id":2,"type":"Art"}]
                        current_category:
                            type: integer
                            example: 2
                        total_questions:
                            type: integer
                            example: 24
                        questions:
                            type: array
                            items:
                                $ref: '#/definitions/Question'
                            example: [{
                                "id":5,
                                "question":"Whose autobiography is entitled 'I know why the caged bird sings?'",
                                "answer":"Maya Angelou",
                                "difficulty":2,
                                "category":4
                                }
                            ]

        """

        # get page from args
        page = request.args.get("page")

        # actual page for pagination...
        page_int = 0

        # convert to int
        if page:
            page_int = int(page)
        else:
            page_int = 1

        # set questions per page
        per_page = QUESTIONS_PER_PAGE

        # get questions for current page (paginated)
        questions = Question.query.order_by(Question.id.asc()).paginate(
            page_int, per_page, error_out=True
        )

        # formatted questions in array
        formatted_questions = [q.format() for q in questions.items]

        # get all categories
        # categories = Category.query.all()
        categories = query_all_categories()

        current_category = Category.query.order_by(Category.type.asc()).first()

        # for some reason need to return as a dict not list/array?
        # formatted_categories = {cat.id: cat.type for cat in categories}

        # return as JSON
        return jsonify(
            questions=formatted_questions,
            total_questions=questions.total,
            categories=categories,
            current_category=current_category.id,
        )

    """
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    """

    @app.route("/api/questions", methods=["POST"])
    def get_questions_by_query():
        # get request data (body)
        body = request.get_json()

        # get searchTerm from body
        query_term = body.get("searchTerm")

        # search result
        query_result = Question.query.filter(
            Question.question.ilike(f"%{query_term}%")
        ).all()

        formatted_result = [q.format() for q in query_result]

        return jsonify({"questions": formatted_result})

    """
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    """

    @app.route("/api/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):

        # page from args
        page = request.args.get("page")

        page_int = 0

        if page:
            page_int = int(page)
        else:
            page_int = 1

        # questions per page for pagination
        per_page = QUESTIONS_PER_PAGE

        category = Category.query.get(category_id)

        if category:
            # get category id as int
            category_id_int = int(category.id)

            questions = Question.query.filter_by(category=category_id_int).paginate(
                page_int, per_page, error_out=True
            )

            # clean up questions for response
            formatted_questions = [q.format() for q in questions.items]

            return jsonify(
                {
                    "questions": formatted_questions,
                    "total_questions": len(questions.items),
                    "current_category": category_id,
                    "categories": query_all_categories(),
                }
            )
        # if category doesn't exist return error
        else:
            return make_response(jsonify({"error": "category does not exist"}), 404)

    """
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.  
    """

    @app.route("/api/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        # get the question by id
        question = Question.query.get(question_id)

        # if question exists, delete it and send a response
        if question:
            question.delete()
            res = make_response(jsonify({}), 204)
            return res

        # else, respond with 404
        res = make_response(jsonify({"error": "question not found"}), 404)
        return res

    """
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    """

    @app.route("/api/questions/create", methods=["POST"])
    def create_question():
        # get body data as json
        body = request.get_json()

        # create new question
        new_question = Question(
            question=body.get("question"),
            answer=body.get("answer"),
            category=body.get("category"),
            difficulty=body.get("difficulty"),
        )

        # insert
        new_question.insert()

        # response
        res = make_response(jsonify(new_question.format()), 201)

        return res

    """
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    """

    """
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app
