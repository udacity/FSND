from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

import os

# Get password from outside of repo

password_path = os.path.dirname(os.path.abspath(__file__)) + '/../../../.dbpassword'
print('password_path: {}'.format(password_path))
with open(password_path) as fp:
    password = fp.read().strip()
print("password: {}".format(password))

# Lesson Exercises

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://frank:{}@localhost:5432/test_sqlalchemy'.format(password)
db = SQLAlchemy(app)

class Person(db.Model):
  __tablename__ = 'persons'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)

db.create_all()

@app.route('/')
def index():
    person = Person.query.first()
    return "hello {}".format(person.name)

if __name__ == '__main__':
    app.run()