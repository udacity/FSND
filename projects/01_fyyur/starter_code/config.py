import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://udacity:abcd1234@localhost:5432/fyyur'

SQLALCHEMY_DATABASE_URI="postgres://udacity:abcd1234@localhost:5432/fyyur"
SQLALCHEMY_TRACK_MODIFICATIONS = True
