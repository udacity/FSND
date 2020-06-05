from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    data = [
            {'description': 'Todo 1'},
            {'description': 'Todo 2'},
            {'description': 'Todo 3'},
            {'description': 'Todo 4'}
            ]
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run()
