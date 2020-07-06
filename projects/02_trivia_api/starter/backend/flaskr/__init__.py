import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
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

    # Create an endpoint to handle GET requests for all available categories.
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories
        }
        return jsonify({
          'success': True,
          'categories': formatted_categories
        })

    # Create an endpoint to handle GET requests for questions,
    # including pagination (every 10 questions).
    # This endpoint should return a list of questions,
    # number of total questions, current category, categories.
    ###########################################################################
    # TEST: At this point, when you start the application.
    # you should see questions and categories generated,
    # 10 questions per page and pagination at the bottom for 3 pages.
    # Clicking on the page numbers should update the questions.

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        print(request.args.get('page'))
        current_questions = paginate_questions(
            request, Question.query.order_by(Question.id).all()
        )
        # Udacity forum https://knowledge.udacity.com/questions/233578
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type for category in categories
        }

        if (len(current_questions) == 0): # if no questions in database return not found
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(Question.query.all()),
            'categories': formatted_categories,
            'currentCategory': None,
        }), 200

    # Create an endpoint to DELETE question using a question ID.
    # TEST: When you click the trash icon next to a question,
    # the question will be removed.
    # This removal will persist in the database and when you refresh the page.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id
            ).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
            })
        except:
            abort(422)

    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.
    # TEST: When you submit a question on the "Add" tab,
    # the form will clear and the question will appear at the end of  last page
    # of the questions list in the "List" tab.

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        
        try:
            if new_question == None or new_answer == None or new_difficulty == None or new_category == None:
                abort(405)
            question = Question(
                question=new_question,
                answer=new_answer,
                difficulty=new_difficulty,
                category=new_category
            )
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
            })
        except:
            abort(422)

    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.
    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # changed the name of the endpoint to avoid doing search and
    # add in the same endpoint.

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        searchTerm = "%{}%".format(body.get('searchTerm', None))

        print('searchterm: ' + searchTerm)

        current_questions = paginate_questions(
            request,
            Question.query.filter(
                Question.question.ilike(searchTerm)
            ).order_by(Question.id).all())

        print(current_questions)
        if (len(current_questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(Question.query.all()),
            'currentCategory': None,

        })

    # Create a GET endpoint to get questions based on category.
    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        current_questions = paginate_questions(
            request,
            Question.query.filter_by(
                category=category_id
            ).order_by(Question.id).all()
        )

        current_category = Category.query.get(category_id)

        if (len(current_questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(Question.query.all()),
            'currentCategory': str(current_category.type)
        })

    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.

    # TEST: In the "Play" tab, after a user selects "All" or a category
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.

    @app.route('/quizzes', methods=['POST'])
    def retrieve_quiz_questions():

        body = request.get_json()
        quiz_category_id = body.get('quiz_category')['id']

        previous_quiz_questions = body.get('previousQuestions')

        print(previous_quiz_questions)
        print(quiz_category_id)

        if previous_quiz_questions is None and quiz_category_id != 0:
            new_quiz_question = Question.query.filter(
              Question.category == quiz_category_id
            ).order_by(func.random()).all()[0].format()
            previous_quiz_questions = [new_quiz_question['id']]
        elif previous_quiz_questions is not None and quiz_category_id != 0:
            new_quiz_question = Question.query.filter(
                Question.category == quiz_category_id,
                Question.id.notin_(previous_quiz_questions)
            ).order_by(func.random())[0].format()
            previous_quiz_questions.append(new_quiz_question['id'])
        elif previous_quiz_questions is None and quiz_category_id == 0:
            new_quiz_question = Question.query.order_by(
                func.random()
            )[0].format()
            previous_quiz_questions = [new_quiz_question['id']]
        elif previous_quiz_questions is not None and quiz_category_id == 0:
            new_quiz_question = Question.query.order_by(
                func.random()
            )[0].format()
            previous_quiz_questions.append(new_quiz_question['id'])

        return jsonify({
          'question': new_quiz_question
        })

    # Create error handlers for all expected errors
    # including 404 and 422.

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "Method not allowed"
            }), 405
            
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Unprocessable"
            }), 422

    @app.errorhandler(500)
    def server_issue(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "Something went wrong!"
            }), 500

    return app
