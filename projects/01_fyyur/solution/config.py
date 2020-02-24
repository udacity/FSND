import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# DONE IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://fyyur_user:fyyur_pwd@localhost:5432/fyyur_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
