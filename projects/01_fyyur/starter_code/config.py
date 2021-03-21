import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL ((Done))
SQLALCHEMY_DATABASE_URI = 'postgresql://muath:raghdoosh0@127.0.0.1:5432/fyyurdb'

### Muath TODO: Extar config parameter to silence the FSADeprecationWarning from flask-sqlalchemy ((Done))
SQLALCHEMY_TRACK_MODIFICATIONS = False