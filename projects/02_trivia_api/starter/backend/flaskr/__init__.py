import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


# questions per page, used for pagination
QPP = 10


def create_app():
    """
    Create app, set up CORS allowing * for origin
    :return: app
    """
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS'
        )
        return response

    @app.route('/categories')
    def retrieve_categories():
        """
        Create an endpoint to handle GET requests
        for all available categories.

        :return: available categories
        """
        categories = Category.query.order_by(Category.type).all()

        if not categories:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {
                category.id: category.type for category in categories
            }
        })

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QPP
        end = start + QPP

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route('/questions')
    def retrieve_questions():
        """
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions,
        number of total questions, current category, categories.

        TEST: At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the bottom of the screen for three pages.
        Clicking on the page numbers should update the questions.
        """
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.type).all()

        if not current_questions:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })

    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        """
        Create an endpoint to DELETE question using a question ID.

        TEST: When you click the trash icon next to a question, the question will be removed.
        This removal will persist in the database and when you refresh the page.
        :param question_id: question ID
        :return: delete question
        """
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)


    @app.route("/questions", methods=['POST'])
    def add_question():
        """
        Create an endpoint to POST a new question,
        which will require the question and answer text,
        category, and difficulty score.

        TEST: When you submit a question on the "Add" tab,
        the form will clear and the question will appear at the end of the last page
        of the questions list in the "List" tab.
        :return:
        """
        body = request.get_json()

        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
            })

        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        """
        Create a POST endpoint to get questions based on a search term.
        It should return any questions for whom the search term
        is a substring of the question.

        TEST: Search by any phrase. The questions list will update to include
        only question that include that string within their question.
        Try using the word "title" to start.
        :return:
        """
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })
        abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        """
        Create a GET endpoint to get questions based on category.

        TEST: In the "List" tab / main screen, clicking on one of the
        categories in the left column will cause only questions of that
        category to be shown.
        :param category_id:
        :return:
        """
        try:
            questions = Question.query.filter(
                Question.category == str(category_id)
            ).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        """
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.

        TEST: In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and shown whether they were correct or not.
        :return:
        """
        try:
            body = request.get_json()

            if not all(req_fields in body for req_fields in ['quiz_category', 'previous_questions']):
                abort(422)

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))
                ).all()
            else:
                category_questions = Question.query.filter_by(category=category['id'])
                available_questions = category_questions.filter(Question.id.notin_(previous_questions)).all()

            new_question = None
            if len(available_questions) > 0:
                new_question = available_questions[random.randrange(0, len(available_questions))].format()

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)

    # error handling
    @app.errorhandler(404)
    def not_found(error):
        """
        Error handler for 404
        :param error:
        :return:
        """
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        """
        Error handler for 422
        :param error:
        :return:
        """
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        """
        Error handler for 400
        :param error:
        :return:
        """
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
