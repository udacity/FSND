from flask import Flask
from models import Category, Question
from flask_sqlalchemy import SQLAlchemy
database_path = "postgresql://postgres@localhost:5432/myTrivia"
app = Flask(__name__)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.app = app
db.init_app(app)


c1 = Category(type="Science")
db.session.add(c1)
db.session.commit()


c1 = Category(type="Art")
db.session.add(c1)
db.session.commit()


c1 = Category(type="Geography")
db.session.add(c1)
db.session.commit()


c1 = Category(type="History")
db.session.add(c1)
db.session.commit()


c1 = Category(type="Entertainment")
db.session.add(c1)
db.session.commit()


c1 = Category(type="Sports")
db.session.add(c1)
db.session.commit()


q1 = Question(question='Whose autobiography is entitled \'I Know Why the Caged Bird Sings\'', answer='Maya Angelou', difficulty=2, category=4)
db.session.add(q1)
db.session.commit()

q1 = Question(question='What boxer\'s original name is Cassius Clay',
              answer='Muhammad Ali', difficulty=1, category=4)
db.session.add(q1)
db.session.commit()


q1 = Question(question='What movie earned Tom Hanks his third straight Oscar nomination, in 1996',
              answer='Apollo 13', difficulty=4, category=5)
db.session.add(q1)
db.session.commit()


q1 = Question(question='What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat',
              answer='Tom Cruise', difficulty=4, category=5)
db.session.add(q1)
db.session.commit()


q1 = Question(question='What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages',
              answer='Edward Scissorhands', difficulty=3, category=5)
db.session.add(q1)
db.session.commit()


q1 = Question(question='Which is the only team to play in every soccer World Cup tournament',
              answer='Brazil', difficulty=3, category=6)
db.session.add(q1)
db.session.commit()


q1 = Question(question='Which country won the first ever soccer World Cup in 1930',
              answer='Uruguay', difficulty=4, category=6)
db.session.add(q1)
db.session.commit()


q1 = Question(question='Who invented Peanut Butter',
              answer='George Washington Carver', difficulty=2, category=4)
db.session.add(q1)
db.session.commit()


q1 = Question(question='What is the largest lake in Africa',
              answer='Lake Victoria', difficulty=2, category=3)
db.session.add(q1)
db.session.commit()


q1 = Question(question='In which royal palace would you find the Hall of Mirrors',
              answer='The Palace of Versailles', difficulty=3, category=3)
db.session.add(q1)
db.session.commit()


q1 = Question(question='The Taj Mahal is located in which Indian city',
              answer='Agra', difficulty=2, category=3)
db.session.add(q1)
db.session.commit()


q1 = Question(question='	Which Dutch graphic artist–initials M C was a creator of optical illusions',
              answer='Escher', difficulty=1, category=2)
db.session.add(q1)
db.session.commit()


q1 = Question(question='La Giaconda is better known as what',
              answer='Mona Lisa	', difficulty=3, category=2)
db.session.add(q1)
db.session.commit()


q1 = Question(question='How many paintings did Van Gogh sell in his lifetime',
              answer='one', difficulty=4, category=2)
db.session.add(q1)
db.session.commit()


q1 = Question(question='Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting',
              answer='Jackson Pollock', difficulty=2, category=2)
db.session.add(q1)
db.session.commit()


q1 = Question(question='What is the heaviest organ in the human body',
              answer='The Liver', difficulty=4, category=1)
db.session.add(q1)
db.session.commit()


q1 = Question(question='Who discovered penicillin',
              answer='Alexander Fleming', difficulty=3, category=1)
db.session.add(q1)
db.session.commit()


q1 = Question(question='Hematology is a branch of medicine involving the study of what',
              answer='Blood', difficulty=4, category=1)
db.session.add(q1)
db.session.commit()


q1 = Question(question='Which dung beetle was worshipped by the ancient Egyptians',
              answer='Scarab', difficulty=4, category=4)
db.session.add(q1)
db.session.commit()
