import os, json
from sqlalchemy import Column, Integer, String, Date, create_engine
from flask_sqlalchemy import SQLAlchemy

DB_PATH = os.environ['DATABASE_URL']

db = SQLAlchemy()

def setup_db(app, database_path = DB_PATH):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class Actor(db.Model):
    __tablename__ = 'actor'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)

    def __init__(self, id, name, age, gender):
        self.name = name
        self.age = age
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

class Movie(db.Model):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key = True)
    title = Column(String)
    releaseDate = Column(Date)

    def __init__(self, id, title, releaseDate):
        self.title = title
        self.releaseDate = releaseDate

    def add(self):
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
      'releaseDate': self.releaseDate    }

