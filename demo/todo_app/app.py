import os
import sys
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

# Get password from outside of repo  
password_path = os.path.dirname(os.path.abspath(__file__)) + '/../../../.dbpassword' 
print('password_path: {}'.format(password_path)) 
with open(password_path) as fp:
    password = fp.read().strip() 
print("password: {}".format(password))


# application initialization
app = Flask(__name__, static_url_path="", static_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://frank:{}@localhost:5432/todoapp'.format(password)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# connect db and app
db = SQLAlchemy(app)

# connect app and db to migration utility
migrate = Migrate(app, db)


# model definition
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_lists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} description: {self.description} completed: {self.completed} list_id: {self.list_id}>'

    @property
    def dictionary(self):
        return {
            'id': self.id,
            'description': self.description,
            'completed': self.completed,
            'list_id': self.list_id
        }


class TodoList(db.Model):
    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)  # backref is arbitrary?

    def __repr__(self):
        return f'<TodoList {self.id} name: {self.name}>'

    @property
    def dictionary(self):
        return {
            'id': self.id,
            'name': self.name,
            'todos': [todo.dictionary for todo in Todo.query.filter(Todo.list_id == self.id)]
        }


# When using flask db migrate we do not need to do db.create_all()
# db.create_all()


# routes
@app.route('/')
def index():
    data = dict()
    todolists = TodoList.query.all()
    if len(todolists) > 0:
        data['todolists'] = todolists
        todolist = todolists[0]
        data['todolist'] = todolist
        data['todos'] = Todo.query.filter(Todo.list_id == todolist.id)
    return render_template('index.html', data=data)


@app.route('/api/todolist', methods=['POST'])
def get_todolist():
    error = False
    body = {}
    list_id = request.get_json().get('id')
    todolist = TodoList.query.get(list_id)

    print(f'sending todolist: {todolist}')
    print(f'todolist.dictionary: {todolist.dictionary}')

    if todolist:
        body['todolist'] = todolist.dictionary
    else:
        error = True

    if not error:
        return jsonify(body)
    else:
        return abort(400)


@app.route('/api/todo/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json().get('description')
        list_id = request.get_json().get('list_id')
        if description and list_id:
            new_todo = Todo(description=description, list_id=list_id)
            db.session.add(new_todo)
            db.session.commit()
            body['description'] = new_todo.description
            body['id'] = new_todo.id
            body['completed'] = new_todo.completed
        else:
            error = True
    except:
        error = True
        db.session.rollback()
        print(sys.exec_info())
    finally:
        db.session.close()
    if not error:
        return jsonify(body)
    else:
        return abort(400)


@app.route('/api/todo/delete', methods=['POST'])
def delete_todo():
    error = False
    body = {}
    try:
        _id = request.get_json().get('id')
        if _id:
            todo = Todo.query.get(_id)
            db.session.delete(todo)
            db.session.commit()
            body['id'] = todo.id
            body['success'] = True
        else:
            error = True
    except:
        error = True
        db.session.rollback()
        print(sys.exec_info())
    finally:
        db.session.close()
    if not error:
        return jsonify(body)
    else:
        return abort(400)


@app.route('/api/todo/completed', methods=['POST'])
def set_todo_completed():
    error = False
    body = {}
    try:
        completed = request.get_json().get('completed')
        _id = request.get_json().get('id')
        if _id and isinstance(completed, bool):
            todo = Todo.query.get(_id)
            todo.completed = completed
            db.session.commit()
            body['completed'] = todo.completed
            body['id'] = todo.id
        else:
            error = True
    except:
            error = True
            db.session.rollback()
            print(sys.exec_info())
    finally:
        db.session.close()
    if not error:
        return jsonify(body)
    else:
        return abort(400)



if __name__ == '__main__':
    app.run()
