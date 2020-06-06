import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

# Get password from outside of repo  
password_path = os.path.dirname(os.path.abspath(__file__)) + '/../../../.dbpassword' 
print('password_path: {}'.format(password_path)) 
with open(password_path) as fp:
    password = fp.read().strip() 
print("password: {}".format(password))


# application initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://frank:{}@localhost:5432/lesson5'.format(password) 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# model definition
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}'


db.create_all()


# routes
@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())


@app.route('/create', methods=['POST'])
def create_todo():
    description = request.get_json().get('description')
    if description:
        new_todo = Todo(description=description)
        db.session.add(new_todo)
        db.session.commit()
    return jsonify({
        'description': new_todo.description
    })


if __name__ == '__main__':
    app.run()
