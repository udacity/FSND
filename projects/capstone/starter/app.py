import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  CORS(app)

  return app

app = create_app()

@app.route('/')
def index():
  return("Hello worlds")

if __name__ == '__main__':
    app.run(debug=True)