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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Person(db.Model):
  __tablename__ = 'persons'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)

  def __repr__(self):
    return f'<Person ID: {self.id}, name: {self.name}>'

db.create_all()

@app.route('/')
def index():
    new_bob = Person(name='Bob')
    another_bob = Person(name='Bobby')
    a_different_bob = Person(name='Bobera')
    wow_more_bob = Person(name='Bo\'b')
    still_bob = Person(name='Bobb')
    just_bob = Person(name='bob')
    db.session.add_all([new_bob, a_different_bob, 
        another_bob, wow_more_bob, still_bob, just_bob])
    db.session.commit()
    
    a = strung_out(Person.query.filter_by(name='Bob').all()  )
    b = strung_out(Person.query.filter(Person.name.like("%{}%".format('b'))).all()  )
    c = strung_out(Person.query.filter(Person.name.like("%{}%".format('b'))).limit(5).all()  )
    d = strung_out(Person.query.filter(Person.name.ilike("%{}%".format('b'))).limit(5).all()  )
    e = strung_out(Person.query.filter_by(name='Bob').count()  )
    returns = '\n'.join([a,b,c,d,e])
    return returns

def strung_out(this_list):
    if isinstance(this_list, list):
        return '\n'.join([ str(item) for item in this_list])
    else:
        return '{}'.format(this_list)


if __name__ == '__main__':
    app.run()