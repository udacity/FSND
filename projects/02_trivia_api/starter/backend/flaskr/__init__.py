import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# paginate questions function


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


# create and configure the app
def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={'/': {'origins': '*'}})

    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Create an endpoint to handle GET requests
    # for all available categories.
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # abort 404 error handler
        if (len(categories_dict) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    # Create an endpoint to handle GET requests for questions,
    # including pagination (every 10 questions).
    # This endpoint should return a list of questions,
    # number of total questions, current category, categories.
    @app.route('/questions')
    def get_questions():
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # abort 404 error handler
        if (len(current_questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        })

    # Create an endpoint to DELETE question using a question ID.
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            # retrieve the question to be deleted
            question = Question.query.filter_by(id=id).one_or_none()

            # abort 422 error handler
            if question is None:
                abort(422)

            # delete the question
            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })

        except Exception as e:
            # abort 422 error handler
            abort(422)

    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.
    @app.route('/questions', methods=['POST'])
    def submit_question():
        body = request.get_json()
        # retrieve new data
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        # check if data exists
        if ((new_question is None) or (new_answer is None)
                or (new_difficulty is None) or (new_category is None)):
            abort(422)

        try:
            # insert new question
            question = Question(question=new_question,
                                answer=new_answer,
                                difficulty=new_difficulty,
                                category=new_category)
            question.insert()

            # get all questions and paginate
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'question_created': question.question,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except Exception as e:
            # abort 422 error handler
            abort(422)

    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        # retrieve searched string
        searched_question = body.get('searchTerm')

        # query the database using search string
        selection = Question.query.filter(
            Question.question.ilike(f'%{searched_question}%')).all()

        # abort 404 error handler
        if (len(selection) == 0):
            abort(404)

        # paginate the search results
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection)
        })

    # Create a GET endpoint to get questions based on category.
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        # retrieve category
        category = Category.query.filter_by(id=id).one_or_none()

        # abort 400 error handler
        if (category is None):
            abort(400)

        # retrieve all questions for the coresponding category
        selection = Question.query.filter_by(category=category.id).all()

        # paginate the question results
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': category.type
        })

    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()

        # retrieve the previous questions
        previous_questions = body.get('previous_questions')

        # retrieve the category
        category = body.get('quiz_category')

        # abort 400 error handler
        if ((category is None) or (previous_questions is None)):
            abort(400)

        # load questions for all categories or based on a selected category
        if (category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        # get total number of questions
        total = len(questions)

        # random generator
        def randomize_question():
            return questions[random.randint(0, len(questions)-1)]

        # checks if question was previously picked
        def already_picked(question):
            picked = False
            for q in previous_questions:
                if (q == question.id):
                    picked = True

            return picked

        # pick a random question
        question = randomize_question()

        # pick another question if current selection was previously used
        while (already_picked(question)):
            question = randomize_question()

            # if all questions exhausted then return without question
            if (len(previous_questions) == total):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
