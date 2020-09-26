import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import math
from sqlalchemy import or_

from models import setup_db, Question, Category, dbSessionClose, dbSessionRollback

QUESTIONS_PER_PAGE = 10
CATEGORIES_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    TODO Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resource={r"/*": {"origins": "*"}})

    """
    TODO Done: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    TODO Done : 
    Create an endpoint to handle GET requests 
    for all available categories.
    """

    @app.route("/categories")
    def getCategories():
        categories = Category.query.order_by(Category.id).all()
        displayCategories = {category.id: category.type for category in categories}

        if len(displayCategories) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "categories": displayCategories,
                "total_categories": len(categories),
            }
        )

    """
    TODO Done: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    """

    @app.route("/questions")
    def getQuestions():
        questions = Question.query.order_by(Question.id).all()
        displayQuestions = paginate_questions(request, questions)
        categories = Category.query.all()
        displayCategories = {category.id: category.type for category in categories}
        if len(displayQuestions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": displayQuestions,
                "total_questions": len(Question.query.all()),
                "categories": displayCategories,
                "current_category": None,
            }
        )

    """
    TODO Done: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    """

    @app.route("/questions/<int:index>", methods=["DELETE"])
    def deleteQuestion(index):
        error = False
        try:
            question = Question.query.get(index)
            if question is None:
                abort(404)
            question.delete()

            questionList = Question.query.all()
            lastPage = endPage(questionList)
        except Exception:
            dbSessionRollback()
            error = True
            print(sys.exc_info())
        finally:
            dbSessionClose()
        if error:
            abort(422)
        else:
            return jsonify({"success": True, "id": index, "lastPage": lastPage})

    """
    TODO Done: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    """

    @app.route("/questions", methods=["POST"])
    def createQuestion():
        payload = request.json
        error = False
        body = {}
        try:
            question = payload["question"]
            answer = payload["answer"]
            difficulty = payload["difficulty"]
            category = payload["category"]
            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty,
            )
            question.insert()
            body["id"] = question.id
        except Exception:
            dbSessionRollback()
            error = True
            print(sys.exc_info())
        finally:
            dbSessionClose()
        if error:
            abort(400)
        else:
            return jsonify(body)

    """
    TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        searchTerm = request.json["searchTerm"]
        searchResult = Question.query.filter(
            Question.question.ilike("%" + searchTerm + "%")
        ).all()
        displayQuestions = [question.format() for question in searchResult]
        # displayQuestions = paginate_questions(request, searchResult)
        categories = Category.query.all()
        displayCategories = {category.id: category.type for category in categories}

        if len(displayQuestions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": displayQuestions,
                "total_questions": len(searchResult),
                "current_category": None,
            }
        )

    """
    TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    """

    @app.route("/categories/<int:index>/questions", methods=["GET"])
    def getQuestionsByCategory(index):
        category = Category.query.get(index)
        questions = Question.query.filter(Question.category == index).all()
        questions_formatted = [question.format() for question in questions]
        if len(questions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": questions_formatted,
                "total_questions": len(questions),
                "current_category": category.format(),
            }
        )

    """
    TODO Done: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    """

    @app.route("/quizzes", methods=["POST"])
    def playQuiz():
        try:
            payload = request.json
            prevQuestions = payload["previous_questions"]
            quizCategory = payload["quiz_category"]
            nextQuestionChoices = Question.query.filter(
                ~Question.id.in_(prevQuestions),
                or_(Question.category == quizCategory["id"], quizCategory["id"] == 0),
            ).all()
            if len(nextQuestionChoices) > 0:
                currentQuestion = random.choice(nextQuestionChoices).format()
            else:
                currentQuestion = None

            return jsonify({"success": True, "question": currentQuestion})
        except Exception:
            abort(400)

    """
    TODO Done: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    return app


##TODO : move these helper functions to another file


def paginate_questions(request, collection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in collection]
    return questions[start:end]


def endPage(collection):
    return math.ceil(len(collection) / QUESTIONS_PER_PAGE)
