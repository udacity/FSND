import os

from sqlalchemy import Column, String, Integer, Date, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_path = os.environ.get('DATABASE_URL')
if not database_path:
    database_name = "agency"
    database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app) - binds the flask application and SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Movies
have title and release date
'''


class Movie(db.Model):
    __tablename__ = 'Movies'

    id = db.Column(Integer, primary_key=True)
    title = db.Column(String, )
    release_date = db.Column(Date)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

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
            'title': self.title,
            'release_date': self.release_date
        }


'''
Actors
have name, age, and gender
'''


class Actor(db.Model):
    __tablename__ = 'Actors'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String)
    age = db.Column(Integer)
    gender = db.Column(String)

    def __init__(self, name, age, gender):
        self.name = name,
        self.age = age,
        self.gender = gender

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
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }
