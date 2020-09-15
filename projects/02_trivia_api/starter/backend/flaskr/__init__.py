import os
from flask import Flask, request, abort, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # db init
    setup_db(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS"
        )
        response.headers.add("Access-Control-Allow-Credentials", "true")

        return response

    @app.route("/api/categories")
    def get_categories():
        """ 
        endpoint for retrieving all question categories
        """

        # get all categories
        try:
            categories = query_all_categories()

            res = {"categories": categories}

            return jsonify(res)
        except:
            abort(404)

    def query_all_categories():
        # decoupled from get_categories so it can be used elsewhere
        """Query to get all categories. 

        Returns:
            List of all categories

        """

        categories = Category.query.all()
        formatted_categories = {cat.id: cat.type for cat in categories}
        return formatted_categories

    @app.route("/api/questions")
    def get_questions():
        """
        endpoint for retrieving all questions
        """
        try:
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

            current_category = Category.query.order_by(
                Category.type.asc()
            ).first()

            # for some reason need to return as a dict not list/array?
            # formatted_categories = {cat.id: cat.type for cat in categories}

            # return as JSON
            return jsonify(
                questions=formatted_questions,
                total_questions=questions.total,
                categories=categories,
                current_category=current_category.id,
            )
        except:
            abort(404)

    @app.route("/api/questions", methods=["POST"])
    def get_questions_by_query():
        """
        endpoint to retrieve a question based on query term
        """

        # get request data (body)
        body = request.get_json()

        if body is None:
            abort(422)

        # get searchTerm from body
        query_term = body.get("searchTerm")

        # search result
        query_result = Question.query.filter(
            Question.question.ilike(f"%{query_term}%")
        ).all()

        formatted_result = [q.format() for q in query_result]

        return jsonify({"questions": formatted_result})

    @app.route("/api/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        """
        endpoint to retrieve questions by category
        """

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

            questions = Question.query.filter_by(
                category=category_id_int
            ).paginate(page_int, per_page, error_out=True)

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
            abort(404)

    @app.route("/api/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """
        delete question by question_id
        """

        # get the question by id
        question = Question.query.get(question_id)

        # if question exists, delete it and send a response
        if question:
            question.delete()
            res = make_response(jsonify({}), 204)
            return res
        else:
            abort(404)

    @app.route("/api/questions/create", methods=["POST"])
    def create_question():
        # get body data as json
        body = request.get_json()

        if body is None:
            abort(422)

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

    @app.route("/api/quizzes", methods=["POST"])
    def play_quiz():

        # front-end state for reference
        # this.state = {
        #         quizCategory: null,
        #         previousQuestions: [],
        #         showAnswer: false,
        #         categories: {},
        #         numCorrect: 0,
        #         currentQuestion: {},
        #         guess: '',
        #         forceEnd: false
        #         }

        # get category and previous ques params
        body = request.get_json()

        print(body)

        if body is None:
            # if no body then set init values
            previous_questions = []
            quiz_category = {}
        else:
            previous_questions = body.get("previous_questions", [])
            quiz_category = body.get("quiz_category", {})

        if quiz_category is None:
            # get all questions if there is no category set
            questions = Question.query.all()
        else:
            # get questions for current category
            questions = (
                Question.query.order_by(Question.id)
                .filter_by(category=str(quiz_category["id"]))
                .all()
            )

        # if no previous questions, get the first question
        if len(previous_questions) == 0:
            question = questions[0]
        else:
            question = next(
                (q for q in questions if q.id not in previous_questions), None
            )

        # format it for res
        if question is None:
            result_question = ""
            category = ""
        else:
            result_question = question.format()
            category = (
                Category.query.filter_by(id=str(result_question["category"]))
                .first()
                .format()
            )

        # return as json
        return jsonify({"question": result_question, "quiz_category": category})

    # error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "unprocessable"}
            ),
            422,
        )

    return app
