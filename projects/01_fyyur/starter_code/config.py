import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost:5432/fyyur'

# Turn off SQLAlchemy modification tracking to avoid deprecation warning and overhead
SQLALCHEMY_TRACK_MODIFICATIONS = False
