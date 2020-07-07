import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json


db = SQLAlchemy()


DEFAULT_DATABASE_NAME = 'trivia'
'''
make_db_uri()
        performs database setup tasks. 
'''


def make_db_uri(database_name=DEFAULT_DATABASE_NAME):
    basedir = os.path.abspath(os.path.dirname(__file__))
    password_path = basedir + '/.secrets'
    print('password_path: {}'.format(password_path))

    data = dict()
    if os.path.isfile(password_path):
        with open(password_path, 'r') as json_file:
            data = json.load(json_file)
            print(f'data: {data}')
    else:
        print('No .secrets file detected.')

    username = data.get('username', 'postgres')
    password = data.get('password')
    host = data.get('host', 'localhost')
    port = data.get('port', '5432')
    database_name = data.get('database_name', database_name)

    if password:
        userpass = '{}:{}@'.format(username, password)
    elif username:
        userpass = '{}@'.format(username)
    else:
        userpass = ''

    return f'postgresql://{userpass}{host}:{port}/{database_name}'


'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=None, database_name=DEFAULT_DATABASE_NAME):
    if database_path is None:
        database_path = make_db_uri(database_name=database_name)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Question
'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


'''
Category

'''
class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }