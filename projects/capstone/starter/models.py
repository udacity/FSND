import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

# database_name = "casting-agency"
# database_path = "postgres://postgres:stemed@{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://flgwzfaftykbvd:73b2bc943dfdfcc89c034d1e3aabac04d9877b38dbf89b6479fa35e1844f340d@ec2-52-73-247-67.compute-1.amazonaws.com:5432/dak2rk0fbi1b6l"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(db.Integer, primary_key=True)
    title = Column(db.String(50), nullable=False)
    release_date = Column(db.String(4), nullable=False)
    
    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def format(self):
        return{
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }

class Actor(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }
